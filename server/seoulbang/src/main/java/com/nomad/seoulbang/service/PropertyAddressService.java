package com.nomad.seoulbang.service;

import com.nomad.seoulbang.client.KakaoAddressClient;
import com.nomad.seoulbang.exception.CustomException;
import com.nomad.seoulbang.exception.ErrorCode;
import com.nomad.seoulbang.repository.PropertyRepository;
import lombok.Getter;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
@Slf4j
public class PropertyAddressService {
    
    // 상수 정의
    private static final String ADDRESS_FIELD = "address";
    private static final String LOT_NUMBER_FIELD = "lot_number";
    private static final String LONGITUDE_FIELD = "lon";
    private static final String LATITUDE_FIELD = "lat";
    private static final String ID_FIELD = "id";
    
    private final PropertyRepository propertyRepository;
    private final KakaoAddressClient kakaoAddressClient;

    @Value("${BATCH_SIZE:100}")
    private int batchSize;

    @Transactional
    public void batchUpdateMissingAddresses() {
        log.info("주소 정보 업데이트 작업 시작");
        
        try {
            List<Map<String, Object>> properties = fetchPropertiesRequiringUpdate();
            
            if (properties.isEmpty()) {
                log.info("업데이트할 주소 정보가 없습니다.");
                return;
            }

            BatchUpdateParams batchParams = prepareBatchUpdateParams(properties);
            int totalUpdates = executeAddressBatchUpdates(batchParams);
            
            log.info("주소 정보 업데이트 작업 완료: 총 {}건 업데이트", totalUpdates);
            
        } catch (Exception e) {
            log.error("주소 정보 업데이트 작업 중 오류 발생", e);
            throw new CustomException(ErrorCode.INTERNAL_SERVER_ERROR, e);
        }
    }

    private List<Map<String, Object>> fetchPropertiesRequiringUpdate() {
        try {
            return propertyRepository.findPropertiesBasicInfo();
        } catch (Exception e) {
            log.error("매물 기본 정보 조회 실패", e);
            throw new CustomException(ErrorCode.INTERNAL_SERVER_ERROR, "매물 기본 정보 조회에 실패했습니다.");
        }
    }

    @Getter
    private static class BatchUpdateParams {
        private final List<Object[]> addressBatchParams = new ArrayList<>();
        private final List<Object[]> lotNumberBatchParams = new ArrayList<>();
        private final List<Object[]> combinedBatchParams = new ArrayList<>();

        public boolean isEmpty() {
            return addressBatchParams.isEmpty() && lotNumberBatchParams.isEmpty() && combinedBatchParams.isEmpty();
        }

        public int getTotalSize() {
            return addressBatchParams.size() + lotNumberBatchParams.size() + combinedBatchParams.size();
        }
    }

    private BatchUpdateParams prepareBatchUpdateParams(List<Map<String, Object>> properties) {
        BatchUpdateParams params = new BatchUpdateParams();
        
        for (Map<String, Object> property : properties) {
            try {
                preparePropertyParam(property, params);
            } catch (Exception e) {
                Long propertyId = extractPropertyId(property);
                log.warn("매물 ID={} 주소 정보 준비 중 오류 발생, 건너뜀", propertyId, e);
            }
        }
        
        log.info("배치 업데이트 준비 완료: 총 {}건", params.getTotalSize());
        return params;
    }

    private void preparePropertyParam(Map<String, Object> property, BatchUpdateParams params) {
        Long propertyId = extractPropertyId(property);
        CoordinateInfo coordinates = extractCoordinates(property);

        if (!coordinates.isValid()) {
            log.debug("매물 ID={} 좌표 정보 누락, 건너뜀", propertyId);
            return;
        }

        AddressInfo addressInfo = fetchAddressInfo(property, coordinates);
        addParamsIfNeeded(propertyId, addressInfo, params);
    }

    private Long extractPropertyId(Map<String, Object> property) {
        Object idObj = property.get(ID_FIELD);
        if (idObj instanceof Number) {
            return ((Number) idObj).longValue();
        }
        throw new CustomException(ErrorCode.INVALID_INPUT_VALUE, "유효하지 않은 매물 ID");
    }

    private CoordinateInfo extractCoordinates(Map<String, Object> property) {
        Double longitude = (Double) property.get(LONGITUDE_FIELD);
        Double latitude = (Double) property.get(LATITUDE_FIELD);
        return new CoordinateInfo(longitude, latitude);
    }

    private AddressInfo fetchAddressInfo(Map<String, Object> property, CoordinateInfo coordinates) {
        String existingAddress = (String) property.get(ADDRESS_FIELD);
        String existingLotNumber = (String) property.get(LOT_NUMBER_FIELD);
        
        try {
            Map<String, String> newAddressData = kakaoAddressClient.getAddressByCoordinates(
                    coordinates.longitude(), coordinates.latitude());
            
            return new AddressInfo(
                    existingAddress, 
                    existingLotNumber,
                    newAddressData.get("address"), 
                    newAddressData.get("lotNumber")
            );
        } catch (Exception e) {
            log.warn("카카오 주소 API 호출 실패: 좌표=({}, {})", 
                    coordinates.longitude(), coordinates.latitude(), e);
            throw new CustomException(ErrorCode.KAKAO_API_ERROR, e);
        }
    }

    private record CoordinateInfo(Double longitude, Double latitude) {
        public boolean isValid() {
            return longitude != null && latitude != null;
        }
    }

    @Getter
    private static class AddressInfo {
        private final String existingAddress;
        private final String existingLotNumber;
        private final String newAddress;
        private final String newLotNumber;

        public AddressInfo(String existingAddress, String existingLotNumber, 
                          String newAddress, String newLotNumber) {
            this.existingAddress = existingAddress;
            this.existingLotNumber = existingLotNumber;
            this.newAddress = newAddress;
            this.newLotNumber = newLotNumber;
        }

        public boolean needsAddressUpdate() {
            return isNullOrEmpty(existingAddress) && hasValidNewAddress();
        }

        public boolean needsLotNumberUpdate() {
            return isNullOrEmpty(existingLotNumber) && hasValidNewLotNumber();
        }

        private boolean hasValidNewAddress() {
            return newAddress != null && !newAddress.trim().isEmpty();
        }

        private boolean hasValidNewLotNumber() {
            return newLotNumber != null && !newLotNumber.trim().isEmpty();
        }

        private boolean isNullOrEmpty(String str) {
            return str == null || str.trim().isEmpty();
        }
    }

    private void addParamsIfNeeded(Long propertyId, AddressInfo info, BatchUpdateParams params) {
        boolean needsAddressUpdate = info.needsAddressUpdate();
        boolean needsLotNumberUpdate = info.needsLotNumberUpdate();

        if (needsAddressUpdate && needsLotNumberUpdate) {
            addCombinedParam(propertyId, info, params);
        } else {
            addSingleParamsIfNeeded(propertyId, info, needsAddressUpdate, needsLotNumberUpdate, params);
        }
    }

    private void addCombinedParam(Long propertyId, AddressInfo info, BatchUpdateParams params) {
        params.getCombinedBatchParams().add(new Object[]{
                info.getNewAddress(), 
                info.getNewLotNumber(), 
                propertyId
        });
        
        log.debug("매물 ID={} 도로명 주소 및 지번 업데이트 준비: address={}, lot={}", 
                propertyId, info.getNewAddress(), info.getNewLotNumber());
    }

    private void addSingleParamsIfNeeded(Long propertyId, AddressInfo info, 
                                       boolean needsAddressUpdate, boolean needsLotNumberUpdate, 
                                       BatchUpdateParams params) {
        if (needsAddressUpdate) {
            params.getAddressBatchParams().add(new Object[]{info.getNewAddress(), propertyId});
            log.debug("매물 ID={} 도로명 주소 업데이트 준비: {}", propertyId, info.getNewAddress());
        }
        
        if (needsLotNumberUpdate) {
            params.getLotNumberBatchParams().add(new Object[]{info.getNewLotNumber(), propertyId});
            log.debug("매물 ID={} 지번 주소 업데이트 준비: {}", propertyId, info.getNewLotNumber());
        }
    }

    private int executeAddressBatchUpdates(BatchUpdateParams params) {
        if (params.isEmpty()) {
            log.info("업데이트할 주소 정보가 없습니다.");
            return 0;
        }

        int totalUpdates = 0;
        totalUpdates += updateCombinedAddressAndLotNumber(params.getCombinedBatchParams());
        totalUpdates += updateAddressOnly(params.getAddressBatchParams());
        totalUpdates += updateLotNumberOnly(params.getLotNumberBatchParams());
        
        return totalUpdates;
    }

    private int updateCombinedAddressAndLotNumber(List<Object[]> params) {
        if (params.isEmpty()) {
            return 0;
        }

        try {
            propertyRepository.batchUpdateAddressAndLotNumber(params, batchSize);
            log.info("도로명 주소 및 지번 일괄 업데이트 완료: {}건", params.size());
            return params.size();
        } catch (Exception e) {
            log.error("도로명 주소 및 지번 일괄 업데이트 실패: {}건", params.size(), e);
            throw new CustomException(ErrorCode.INTERNAL_SERVER_ERROR, "도로명 주소 및 지번 업데이트에 실패했습니다.");
        }
    }

    private int updateAddressOnly(List<Object[]> params) {
        if (params.isEmpty()) {
            return 0;
        }

        try {
            propertyRepository.batchUpdateAddress(params, batchSize);
            log.info("도로명 주소 일괄 업데이트 완료: {}건", params.size());
            return params.size();
        } catch (Exception e) {
            log.error("도로명 주소 일괄 업데이트 실패: {}건", params.size(), e);
            throw new CustomException(ErrorCode.INTERNAL_SERVER_ERROR, "도로명 주소 업데이트에 실패했습니다.");
        }
    }

    private int updateLotNumberOnly(List<Object[]> params) {
        if (params.isEmpty()) {
            return 0;
        }

        try {
            propertyRepository.batchUpdateLotNumber(params, batchSize);
            log.info("지번 주소 일괄 업데이트 완료: {}건", params.size());
            return params.size();
        } catch (Exception e) {
            log.error("지번 주소 일괄 업데이트 실패: {}건", params.size(), e);
            throw new CustomException(ErrorCode.INTERNAL_SERVER_ERROR, "지번 주소 업데이트에 실패했습니다.");
        }
    }
}