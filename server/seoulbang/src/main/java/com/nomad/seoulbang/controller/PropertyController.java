package com.nomad.seoulbang.controller;

import com.nomad.seoulbang.dto.PropertyDetailResponse;
import com.nomad.seoulbang.service.PropertyService;
import jakarta.validation.constraints.Min;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("api/property")
@RequiredArgsConstructor
@Slf4j
@Validated
public class PropertyController {

    private final PropertyService propertyService;

    @GetMapping("/detail")
    public ResponseEntity<PropertyDetailResponse> getPropertyDetail(
            @RequestParam("property_id") 
            @Min(value = 1, message = "매물 ID는 1 이상이어야 합니다.") 
            Long propertyId) {
        log.info("매물 상세 정보 요청 수신: propertyId={}", propertyId);
        return ResponseEntity.ok(propertyService.getPropertyDetail(propertyId));
    }
}
