package com.nomad.seoulbang.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public record RecommendPropertyResponse(
        @JsonProperty("result") Result result
) {
    @JsonIgnoreProperties(ignoreUnknown = true)
    public record Result(
            int total,
            @JsonProperty("total_pages") int totalPages,
            int page,
            @JsonProperty("page_size") int pageSize,
            List<Property> results
    ) {
        @JsonIgnoreProperties(ignoreUnknown = true)
        public record Property(
                @JsonProperty("property_id") Long propertyId,
                Double score,
                @JsonProperty("commute_min") Double commuteMin,
                String image,
                String address,
                Long deposit,
                @JsonProperty("monthly_rent_cost") Long monthlyRentCost,
                @JsonProperty("maintenance_cost") Long maintenanceCost,
                Double area,
                Integer floor,
                @JsonProperty("property_type") String propertyType,
                String features,
                String direction,
                @JsonProperty("property_number") String propertyNumber,
                @JsonProperty("property_name") String propertyName,
                @JsonProperty("transaction_type") String transactionType,
                @JsonProperty("property_confirmation_date") String propertyConfirmationDate, // 또는 LocalDate
                @JsonProperty("rooms_bathrooms") String roomsBathrooms,
                Boolean duplex,
                @JsonProperty("total_floor") Integer totalFloor,
                @JsonProperty("room_type") String roomType,
                @JsonProperty("parking_spaces") Integer parkingSpaces,
                @JsonProperty("elevator_count") Integer elevatorCount,
                @JsonProperty("approval_date") String approvalDate, // 또는 LocalDate
                @JsonProperty("cctv_count") Integer cctvCount,
                @JsonProperty("infra_count") Integer infraCount,
                @JsonProperty("avg_cctv_distance") Double avgCctvDistance,
                @JsonProperty("avg_infra_distance") Double avgInfraDistance,
                @JsonProperty("bus_count") Integer busCount,
                @JsonProperty("subway_count") Integer subwayCount,
                @JsonProperty("avg_bus_stop_distance") Double avgBusStopDistance,
                @JsonProperty("avg_subway_distance") Double avgSubwayDistance,
                @JsonProperty("infra_score") Double infraScore,
                @JsonProperty("security_score") Double securityScore,
                @JsonProperty("transport_score") Double transportScore,
                @JsonProperty("quiet_score") Double quietScore,
                @JsonProperty("youth_score") Double youthScore,
                @JsonProperty("commute_score") Double commuteScore
        ) {}
    }
}
