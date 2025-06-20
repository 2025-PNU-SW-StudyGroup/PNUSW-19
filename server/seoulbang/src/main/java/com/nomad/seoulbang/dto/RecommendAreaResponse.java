package com.nomad.seoulbang.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;
import java.util.Map;

public record RecommendAreaResponse(
        @JsonProperty("recommended_area")
        List<Area> recommendedArea,
        @JsonProperty("job_location")
        List<Double> jobLocation
) {
    @JsonIgnoreProperties(ignoreUnknown = true)
    public record Area(
            @JsonProperty("avg_scores") Map<String, Double> avgScores,
            @JsonProperty("avg_total_score") Double avgTotalScore,
            @JsonProperty("dong_list") List<Dong> dongList,
            @JsonProperty("gu") String gu,
            @JsonProperty("gu_code") String guCode,
            @JsonProperty("total_property_count") Integer totalPropertyCount
    ) {
        @JsonIgnoreProperties(ignoreUnknown = true)
        public record Dong(
                @JsonProperty("dong") String dong,
                @JsonProperty("dong_code") String dongCode,
                @JsonProperty("total_score") Double totalScore,
                @JsonProperty("property_count") Integer propertyCount,
                @JsonProperty("commute_min") Double commuteMin,
                @JsonProperty("commute_score") Double commuteScore,
                @JsonProperty("infra_score") Double infraScore,
                @JsonProperty("quiet_score") Double quietScore,
                @JsonProperty("security_score") Double securityScore,
                @JsonProperty("transport_score") Double transportScore,
                @JsonProperty("youth_score") Double youthScore,
                @JsonProperty("property_ids") List<Long> propertyIds
        ) {}
    }
}
