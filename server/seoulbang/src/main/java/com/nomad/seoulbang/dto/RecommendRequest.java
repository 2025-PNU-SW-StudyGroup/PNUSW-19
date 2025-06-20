package com.nomad.seoulbang.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;

import java.util.List;
import java.util.Map;

public record RecommendRequest(
        @NotNull(message = "나이는 필수 입력 값입니다.")
        @Min(value = 1, message = "나이는 1세 이상이어야 합니다.")
        @Max(value = 200, message = "나이는 200세 이하여야 합니다.")
        Integer age,
        
        @NotBlank(message = "성별은 필수 입력 값입니다.")
        @Pattern(regexp = "^(남성|여성|male|female)$", message = "성별은 '남성', '여성', 'male', 'female' 중 하나여야 합니다.")
        String gender,
        
        @NotBlank(message = "주소는 필수 입력 값입니다.")
        @Size(max = 500, message = "주소는 500자를 초과할 수 없습니다.")
        String address,
        
        @NotNull(message = "교통수단은 필수 입력 값입니다.")
        @NotEmpty(message = "교통수단을 최소 하나 이상 선택해야 합니다.")
        @Size(max = 10, message = "교통수단은 최대 10개까지 선택할 수 있습니다.")
        List<@NotBlank(message = "교통수단 항목은 공백일 수 없습니다.") String> transportation,

        Map<String, Object> budget,
        List<String> priority,
        Integer max_commute_min
) {}
