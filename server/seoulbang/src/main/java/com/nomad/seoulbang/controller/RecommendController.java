package com.nomad.seoulbang.controller;

import com.nomad.seoulbang.dto.RecommendAreaResponse;
import com.nomad.seoulbang.dto.RecommendPropertyRequest;
import com.nomad.seoulbang.dto.RecommendPropertyResponse;
import com.nomad.seoulbang.dto.RecommendRequest;
import com.nomad.seoulbang.service.RecommendService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("api/recommend")
@RequiredArgsConstructor
@Slf4j
public class RecommendController {

    private final RecommendService recommendService;

    @PostMapping("/area")
    public ResponseEntity<RecommendAreaResponse> recommendArea(@Valid @RequestBody RecommendRequest request) {
        log.info("지역 추천 요청 수신: address={}, age={}", request.address(), request.age());
        return recommendService.recommendArea(request);
    }

    @PostMapping("/property")
    public ResponseEntity<RecommendPropertyResponse> recommendProperty(@Valid @RequestBody RecommendPropertyRequest request) {
        log.info("매물 추천 요청 수신: dong={}, page={}", request.dong(), request.page());
        return recommendService.recommendProperty(request);
    }
}
