package com.nomad.seoulbang.service;

import com.nomad.seoulbang.exception.CustomException;
import com.nomad.seoulbang.exception.ErrorCode;
import com.nomad.seoulbang.repository.PropertyRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class PropertyResidentialAreaService {
    
    // 상수 정의
    private static final String ID_FIELD = "id";
    private static final String LONGITUDE_FIELD = "lon";
    private static final String LATITUDE_FIELD = "lat";
    
    private final PropertyRepository propertyRepository;

    @Value("${BATCH_SIZE:100}")
    private int batchSize;

    public void updateResidentialAreasForNewProperties() {
        log.info("주거전용지역 업데이트 작업 시작");
        
        try {
            List<Map<String, Object>> properties = fetchPropertiesRequiringResidentialAreaUpdate();
            
            if (properties.isEmpty()) {
                log.info("주거전용지역 업데이트가 필요한 매물이 없습니다.");
                return;
            }

            log.info("주거전용지역 업데이트 대상 매물: {}건", properties.size());
            
            List<Object[]> batchParams = prepareBatchUpdateParams(properties);
            executeResidentialAreaUpdate(batchParams);
            
            log.info("주거전용지역 업데이트 작업 완료");
            
        } catch (Exception e) {
            log.error("주거전용지역 업데이트 작업 중 오류 발생", e);
            throw new CustomException(ErrorCode.INTERNAL_SERVER_ERROR, e);
        }
    }

    private List<Map<String, Object>> fetchPropertiesRequiringResidentialAreaUpdate() {
        try {
            return propertyRepository.findPropertiesMissingResidentialArea(batchSize);
        } catch (Exception e) {
            log.error("주거전용지역 누락 매물 조회 실패", e);
            throw new CustomException(ErrorCode.INTERNAL_SERVER_ERROR, "주거전용지역 누락 매물 조회에 실패했습니다.");
        }
    }

    private List<Object[]> prepareBatchUpdateParams(List<Map<String, Object>> properties) {
        log.debug("주거전용지역 배치 업데이트 파라미터 준비 시작");
        
        List<Object[]> validParams = properties.stream()
                .map(this::createResidentialAreaParam)
                .filter(this::isValidParam)
                .collect(Collectors.toList());
        
        log.info("유효한 주거전용지역 업데이트 파라미터: {}건 (전체 {}건 중)", validParams.size(), properties.size());
        return validParams;
    }

    private Object[] createResidentialAreaParam(Map<String, Object> property) {
        try {
            Long id = extractPropertyId(property);
            CoordinateInfo coordinates = extractCoordinates(property);
            
            if (!coordinates.isValid()) {
                log.debug("매물 ID={} 좌표 정보 누락", id);
                return new Object[]{null, id};
            }
            
            String residentialArea = fetchResidentialArea(coordinates);
            return new Object[]{residentialArea, id};
            
        } catch (Exception e) {
            log.warn("매물 주거전용지역 정보 생성 실패: {}", property.get(ID_FIELD), e);
            return new Object[]{null, property.get(ID_FIELD)};
        }
    }

    private Long extractPropertyId(Map<String, Object> property) {
        Object idObj = property.get(ID_FIELD);
        if (idObj instanceof Number) {
            return ((Number) idObj).longValue();
        }
        throw new CustomException(ErrorCode.INVALID_INPUT_VALUE, "유효하지 않은 매물 ID");
    }

    private CoordinateInfo extractCoordinates(Map<String, Object> property) {
        Double longitude = extractDoubleValue(property, LONGITUDE_FIELD);
        Double latitude = extractDoubleValue(property, LATITUDE_FIELD);
        return new CoordinateInfo(longitude, latitude);
    }

    private Double extractDoubleValue(Map<String, Object> property, String fieldName) {
        Object value = property.get(fieldName);
        if (value instanceof Number) {
            return ((Number) value).doubleValue();
        }
        return null;
    }

    private String fetchResidentialArea(CoordinateInfo coordinates) {
        try {
            return propertyRepository.findResidentialArea(coordinates.longitude(), coordinates.latitude());
        } catch (Exception e) {
            log.warn("주거전용지역 조회 실패: 좌표=({}, {})", coordinates.longitude(), coordinates.latitude(), e);
            return null;
        }
    }

    private boolean isValidParam(Object[] param) {
        return param != null && param.length == 2 && param[0] != null && param[1] != null;
    }

    private void executeResidentialAreaUpdate(List<Object[]> params) {
        if (params.isEmpty()) {
            log.info("업데이트할 주거전용지역 정보가 없습니다.");
            return;
        }

        try {
            propertyRepository.batchUpdateResidentialArea(params);
            log.info("주거전용지역 일괄 업데이트 완료: {}건", params.size());
        } catch (Exception e) {
            log.error("주거전용지역 일괄 업데이트 실패: {}건", params.size(), e);
            throw new CustomException(ErrorCode.INTERNAL_SERVER_ERROR, "주거전용지역 업데이트에 실패했습니다.");
        }
    }

    private record CoordinateInfo(Double longitude, Double latitude) {
        public boolean isValid() {
            return longitude != null && latitude != null;
        }
    }
}
