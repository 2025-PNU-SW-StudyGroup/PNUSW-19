package com.nomad.seoulbang.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.LocalDate;
import java.util.List;

public record PropertyDetailResponse(
        // 매물 기본 정보
        @JsonProperty("property_id") Long propertyId,
        @JsonProperty("address") String address,
        @JsonProperty("longitude") Double longitude,
        @JsonProperty("latitude") Double latitude,
        @JsonProperty("deposit") Long deposit,
        @JsonProperty("monthly_rent_cost") Long monthlyRentCost,
        @JsonProperty("maintenance_cost") Long maintenanceCost,
        @JsonProperty("area") Double area,
        @JsonProperty("floor") Integer floor,
        @JsonProperty("property_type") String propertyType,
        @JsonProperty("features") String features,
        @JsonProperty("direction") String direction,
        @JsonProperty("residential_area") String residentialArea,
        @JsonProperty("lot_number") String lotNumber,
        @JsonProperty("description") String description,
        @JsonProperty("agent_name") String agentName,
        @JsonProperty("agent_office") String agentOffice,
        @JsonProperty("agent_phone") String agentPhone,
        @JsonProperty("agent_address") String agentAddress,
        @JsonProperty("agent_registration_no") String agentRegistrationNo,
        @JsonProperty("property_number") String propertyNumber,
        @JsonProperty("administrative_code") String administrativeCode,
        @JsonProperty("property_name") String propertyName,
        @JsonProperty("transaction_type") String transactionType,
        @JsonProperty("confirmation_type") String confirmationType,
        @JsonProperty("supply_area") Double supplyArea,
        @JsonProperty("property_confirmation_date") LocalDate propertyConfirmationDate,
        @JsonProperty("main_image_url") String mainImageUrl,
        @JsonProperty("rooms_bathrooms") String roomsBathrooms,
        @JsonProperty("duplex") Boolean duplex,
        @JsonProperty("available_move_in_date") String availableMoveInDate,
        @JsonProperty("parking_spaces") Integer parkingSpaces,
        @JsonProperty("total_floor") Integer totalFloor,
        @JsonProperty("room_type") String roomType,
        @JsonProperty("elevator_count") Integer elevatorCount,
        @JsonProperty("household_count") Integer householdCount,
        @JsonProperty("family_count") Integer familyCount,
        @JsonProperty("main_purpose") String mainPurpose,
        @JsonProperty("etc_purpose") String etcPurpose,
        @JsonProperty("structure_code") String structureCode,
        @JsonProperty("approval_date") LocalDate approvalDate,

        // 사진
        @JsonProperty("photos") List<Photo> photos,

        // 태그
        @JsonProperty("tags") List<String> tags,

        // 주변 시설
        @JsonProperty("bus_stops") List<BusStop> busStops,
        @JsonProperty("subways") List<Subway> subways,
        @JsonProperty("cctvs") List<Cctv> cctvs,
        @JsonProperty("rest_food_permits") List<RestFoodPermit> restFoodPermits
) {
    public record Photo(
            @JsonProperty("image_url") String imageUrl,
            @JsonProperty("image_type") String imageType,
            @JsonProperty("order") Integer order
    ) {}

    // 주변 버스정류장
    public record BusStop(
            @JsonProperty("id") Long id,
            @JsonProperty("distance_meters") Double distanceMeters,
            @JsonProperty("stop_name") String stopName,
            @JsonProperty("stop_type") String stopType,
            @JsonProperty("stop_number") Integer stopNumber,
            @JsonProperty("latitude") Double latitude,
            @JsonProperty("longitude") Double longitude,
            @JsonProperty("bus_arrival_info_display_installed") String busArrivalInfoDisplayInstalled
    ) {}

    // 주변 지하철역
    public record Subway(
            @JsonProperty("id") Long id,
            @JsonProperty("distance_meters") Double distanceMeters,
            @JsonProperty("sequence_number") String sequenceNumber,
            @JsonProperty("line_number") String lineNumber,
            @JsonProperty("unique_station_code") String uniqueStationCode,
            @JsonProperty("station_name") String stationName,
            @JsonProperty("latitude") Double latitude,
            @JsonProperty("longitude") Double longitude
    ) {}

    // 주변 CCTV
    public record Cctv(
            @JsonProperty("id") Long id,
            @JsonProperty("distance_meters") Double distanceMeters,
            @JsonProperty("region") String region,
            @JsonProperty("safe_address") String safeAddress,
            @JsonProperty("latitude") Double latitude,
            @JsonProperty("longitude") Double longitude,
            @JsonProperty("cctv_count") Integer cctvCount,
            @JsonProperty("modified_datetime") String modifiedDatetime
    ) {}

    // 주변 음식점 인허가
    public record RestFoodPermit(
            @JsonProperty("id") Long id,
            @JsonProperty("distance_meters") Double distanceMeters,
            @JsonProperty("bplcnm") String bplcnm, // 업소명
            @JsonProperty("sitewhladdr") String sitewhladdr, // 지번주소
            @JsonProperty("rdnwhladdr") String rdnwhladdr,  // 도로명주소
            @JsonProperty("uptaenm") String uptaenm,     // 업태명
            @JsonProperty("mgtno") String mgtno,       // 관리번호
            @JsonProperty("opnsfteamcode") String opnsfteamcode, // 영업소코드
            @JsonProperty("sitearea") String sitearea,    // 면적
            @JsonProperty("sitetel") String sitetel,     // 전화번호
            @JsonProperty("x") Double x,           // 경도
            @JsonProperty("y") Double y            // 위도
    ) {}
}
