package com.nomad.seoulbang.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.nomad.seoulbang.client.BuildingApiClient;
import com.nomad.seoulbang.dto.BuildingInfo;
import com.nomad.seoulbang.dto.LocationInfo;
import com.nomad.seoulbang.exception.CustomException;
import com.nomad.seoulbang.exception.ErrorCode;
import com.nomad.seoulbang.repository.PropertyRepository;
import com.nomad.seoulbang.util.LotNumberParser;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.Map;

@Service
@Slf4j
@RequiredArgsConstructor
public class BuildingInfoService {

    // 상수 정의
    private static final int ADMINISTRATIVE_CODE_LENGTH = 10;
    private static final int SIGUNGU_CODE_END_INDEX = 5;
    private static final String DATE_PATTERN = "yyyyMMdd";

    // JSON 필드명 상수
    private static final String INDOOR_MECHANICAL_PARKING = "indrMechUtcnt";
    private static final String OUTDOOR_MECHANICAL_PARKING = "oudrMechUtcnt";
    private static final String INDOOR_AUTO_PARKING = "indrAutoUtcnt";
    private static final String OUTDOOR_AUTO_PARKING = "oudrAutoUtcnt";
    private static final String PASSENGER_ELEVATOR = "rideUseElvtCnt";
    private static final String EMERGENCY_ELEVATOR = "emgenUseElvtCnt";

    private final BuildingApiClient buildingApiClient;
    private final PropertyRepository propertyRepository;
    private final ObjectProvider<BuildingInfoService> selfProvider;

    @Cacheable(
            value = "buildingInfoCache",
            key = "#sigunguCd + '-' + #bjdongCd + '-' + #bun + '-' + #ji",
            unless = "#result == null"
    )
    public BuildingInfo getOrFetchBuildingInfo(String sigunguCd, String bjdongCd, String bun, String ji) {
        log.info("캐시 미스 - API 호출: {}-{}-{}-{}", sigunguCd, bjdongCd, bun, ji);
        
        JsonNode itemsNode = buildingApiClient.getBuildingInfo(sigunguCd, bjdongCd, bun, ji);
        if (hasValidItems(itemsNode)) {
            return parseBuildingInfo(itemsNode.get(0));
        }
        
        log.warn("건물 정보를 찾을 수 없습니다: {}-{}-{}-{}", sigunguCd, bjdongCd, bun, ji);
        return null;
    }

    public void updateBuildingInfo(Map<String, Object> property) {
        try {
            LocationInfo locationInfo = extractLocationInfo(property);

            if (!locationInfo.isValid()) {
                log.warn("유효하지 않은 위치 정보: property ID={}", property.get("id"));
                return;
            }

            BuildingInfo buildingInfo = fetchBuildingInfoWithCache(locationInfo);
            saveBuildingInfoIfPresent(property, buildingInfo);
            
        } catch (Exception e) {
            log.error("건물 정보 업데이트 실패: property ID={}", property.get("id"), e);
            throw new CustomException(ErrorCode.BUILDING_API_ERROR, e);
        }
    }

    private boolean hasValidItems(JsonNode itemsNode) {
        return itemsNode != null && itemsNode.isArray() && !itemsNode.isEmpty();
    }

    private BuildingInfo fetchBuildingInfoWithCache(LocationInfo locationInfo) {
        return selfProvider.getObject().getOrFetchBuildingInfo(
                locationInfo.sigunguCd(),
                locationInfo.bjdongCd(),
                locationInfo.bun(),
                locationInfo.ji()
        );
    }

    private void saveBuildingInfoIfPresent(Map<String, Object> property, BuildingInfo buildingInfo) {
        if (buildingInfo != null) {
            saveBuildingInfo(property, buildingInfo);
            log.debug("건물 정보 업데이트 완료: property ID={}", property.get("id"));
        } else {
            log.warn("건물 정보가 없어 업데이트를 건너뜁니다: property ID={}", property.get("id"));
        }
    }

    private LocationInfo extractLocationInfo(Map<String, Object> property) {
        String administrativeCode = (String) property.get("administrative_code");
        String lotNumber = (String) property.get("lot_number");
        
        return new LocationInfo(
                extractSigunguCode(administrativeCode),
                extractBjdongCode(administrativeCode),
                LotNumberParser.extractBun(lotNumber),
                LotNumberParser.extractJi(lotNumber)
        );
    }

    private String extractSigunguCode(String administrativeCode) {
        if (administrativeCode != null && administrativeCode.length() == ADMINISTRATIVE_CODE_LENGTH) {
            return administrativeCode.substring(0, SIGUNGU_CODE_END_INDEX);
        }
        return null;
    }

    private String extractBjdongCode(String administrativeCode) {
        if (administrativeCode != null && administrativeCode.length() == ADMINISTRATIVE_CODE_LENGTH) {
            return administrativeCode.substring(SIGUNGU_CODE_END_INDEX, ADMINISTRATIVE_CODE_LENGTH);
        }
        return null;
    }

    private BuildingInfo parseBuildingInfo(JsonNode item) {
        if (item == null || item.isMissingNode()) {
            return null;
        }

        return new BuildingInfo(
                calculateParkingSpaces(item),
                calculateElevatorCount(item),
                getIntValue(item, "hhldCnt"),
                getIntValue(item, "fmlyCnt"),
                getStringValue(item, "mainPurpsCdNm"),
                getStringValue(item, "etcPurps"),
                getStringValue(item, "strctCdNm"),
                parseUseApprovalDate(getStringValue(item, "useAprDay"))
        );
    }

    private int calculateParkingSpaces(JsonNode item) {
        return getIntValue(item, INDOOR_MECHANICAL_PARKING)
                + getIntValue(item, OUTDOOR_MECHANICAL_PARKING)
                + getIntValue(item, INDOOR_AUTO_PARKING)
                + getIntValue(item, OUTDOOR_AUTO_PARKING);
    }

    private int calculateElevatorCount(JsonNode item) {
        return getIntValue(item, PASSENGER_ELEVATOR) + getIntValue(item, EMERGENCY_ELEVATOR);
    }

    private LocalDate parseUseApprovalDate(String useAprDay) {
        if (useAprDay == null || useAprDay.isBlank()) {
            return null;
        }
        
        try {
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern(DATE_PATTERN);
            return LocalDate.parse(useAprDay, formatter);
        } catch (DateTimeParseException e) {
            log.warn("사용승인일 파싱 실패: {}", useAprDay, e);
            return null;
        }
    }

    private void saveBuildingInfo(Map<String, Object> property, BuildingInfo info) {
        Long propertyId = extractPropertyId(property);
        
        propertyRepository.updatePropertyInfo(
                propertyId,
                info.parkingSpaces(),
                info.elevatorCount(),
                info.hhldCnt(),
                info.fmlyCnt(),
                info.mainPurpsCdNm(),
                info.etcPurps(),
                info.strctCdNm(),
                info.useAprDay()
        );
    }

    private Long extractPropertyId(Map<String, Object> property) {
        Object idObj = property.get("id");
        if (idObj instanceof Number) {
            return ((Number) idObj).longValue();
        }
        throw new CustomException(ErrorCode.INVALID_INPUT_VALUE, "유효하지 않은 매물 ID");
    }

    private int getIntValue(JsonNode node, String fieldName) {
        JsonNode fieldNode = node.path(fieldName);
        return fieldNode.isMissingNode() || fieldNode.isNull() ? 0 : fieldNode.asInt();
    }

    private String getStringValue(JsonNode node, String fieldName) {
        JsonNode fieldNode = node.path(fieldName);
        return fieldNode.isMissingNode() || fieldNode.isNull() ? "" : fieldNode.asText();
    }
}
