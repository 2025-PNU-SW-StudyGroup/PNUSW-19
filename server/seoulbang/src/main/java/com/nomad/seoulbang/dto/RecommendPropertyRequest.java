package com.nomad.seoulbang.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;

import java.util.List;
import java.util.Map;

public record RecommendPropertyRequest(
        @Size(max = 100, message = "동 이름은 100자를 초과할 수 없습니다.")
        String dong,
        
        @Size(max = 20, message = "동 코드는 20자를 초과할 수 없습니다.")
        String dong_code,
        
        @DecimalMin(value = "0.0", message = "총점은 0.0 이상이어야 합니다.")
        @DecimalMax(value = "100.0", message = "총점은 100.0 이하여야 합니다.")
        Double total_score,
        
        @Min(value = 0, message = "매물 수는 0 이상이어야 합니다.")
        Integer property_count,
        
        @DecimalMin(value = "0.0", message = "통근 시간은 0.0 이상이어야 합니다.")
        Double commute_min,
        
        @DecimalMin(value = "0.0", message = "인프라 점수는 0.0 이상이어야 합니다.")
        Double infra_score,
        
        @DecimalMin(value = "0.0", message = "보안 점수는 0.0 이상이어야 합니다.")
        Double security_score,
        
        @DecimalMin(value = "0.0", message = "조용함 점수는 0.0 이상이어야 합니다.")
        Double quiet_score,
        
        @DecimalMin(value = "0.0", message = "청년 점수는 0.0 이상이어야 합니다.")
        Double youth_score,
        
        @DecimalMin(value = "0.0", message = "교통 점수는 0.0 이상이어야 합니다.")
        Double transport_score,
        
        @DecimalMin(value = "0.0", message = "통근 점수는 0.0 이상이어야 합니다.")
        Double commute_score,

        List<Long> property_ids,

        UserInput user_input,

        Integer page,
        Integer page_size
) {
    public record UserInput(
            Integer age,
            String gender,

            @NotNull(message = "직장 위치는 필수 입력 값입니다.")
            @Size(min = 2, max = 2, message = "직장 위치는 경도, 위도 2개의 값이어야 합니다.")
            List<@NotNull(message = "좌표 값은 null일 수 없습니다.")
                 @DecimalMin(value = "-180.0", message = "경도는 -180.0 이상이어야 합니다.")
                 @DecimalMax(value = "180.0", message = "경도는 180.0 이하여야 합니다.") Double> job_location,

            @NotNull(message = "교통수단은 필수 입력 값입니다.")
            @NotEmpty(message = "교통수단을 최소 하나 이상 선택해야 합니다.")
            @Size(max = 10, message = "교통수단은 최대 10개까지 선택할 수 있습니다.")
            List<@NotBlank(message = "교통수단 항목은 공백일 수 없습니다.") String> transportation,

            Map<String, Object> budget,
            List<String> priority,
            Integer max_commute_min
    ) {}
}
