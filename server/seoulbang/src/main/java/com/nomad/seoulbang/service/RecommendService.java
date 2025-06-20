package com.nomad.seoulbang.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.nomad.seoulbang.client.KakaoCoordinateClient;
import com.nomad.seoulbang.dto.RecommendAreaResponse;
import com.nomad.seoulbang.dto.RecommendPropertyRequest;
import com.nomad.seoulbang.dto.RecommendPropertyResponse;
import com.nomad.seoulbang.dto.RecommendRequest;
import com.nomad.seoulbang.exception.CustomException;
import com.nomad.seoulbang.exception.ErrorCode;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.*;

@Service
@RequiredArgsConstructor
@Slf4j
public class RecommendService {

    // API 엔드포인트 상수
    private static final String RECOMMEND_AREA_ENDPOINT = "/recommend/area";
    private static final String RECOMMEND_PROPERTY_ENDPOINT = "/recommend/property";
    
    // JSON 필드명 상수
    private static final String RECOMMENDED_AREA_FIELD = "recommended_area";
    
    // 좌표 배열 인덱스 상수
    private static final int LONGITUDE_INDEX = 0;
    private static final int LATITUDE_INDEX = 1;

    private final KakaoCoordinateClient kakaoCoordinateClient;
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    @Value("${recommend.api.url}")
    private String recommendApiUrl;

    public ResponseEntity<RecommendAreaResponse> recommendArea(RecommendRequest request) {
        log.info("지역 추천 요청 시작: address={}", request.address());
        
        try {
            // 1. 주소 → 좌표 변환
            List<Double> jobLocationArray = convertAddressToCoordinates(request.address());
            
            // 2. 추천 API 요청 페이로드 구성
            Map<String, Object> payload = buildRecommendAreaPayload(request, jobLocationArray);
            
            // 3. 추천 API 호출
            ResponseEntity<String> apiResponse = callRecommendAreaApi(payload);
            
            // 4. 응답 파싱 및 결과 생성
            List<RecommendAreaResponse.Area> recommendedAreas = parseRecommendedAreas(apiResponse.getBody());
            RecommendAreaResponse response = new RecommendAreaResponse(recommendedAreas, jobLocationArray);
            
            log.info("지역 추천 요청 완료: 추천 지역 {}개", recommendedAreas.size());
            return ResponseEntity.status(apiResponse.getStatusCode()).body(response);
            
        } catch (CustomException e) {
            throw e;
        } catch (Exception e) {
            log.error("지역 추천 처리 중 예상치 못한 오류 발생", e);
            throw new CustomException(ErrorCode.INTERNAL_SERVER_ERROR, e);
        }
    }

    public ResponseEntity<RecommendPropertyResponse> recommendProperty(RecommendPropertyRequest request) {
        log.info("매물 추천 요청 시작");
        
        try {
            // 1. 추천 매물 API 호출
            ResponseEntity<String> apiResponse = callRecommendPropertyApi(request);
            
            // 2. 응답 파싱
            RecommendPropertyResponse response = parseRecommendPropertyResponse(apiResponse.getBody());
            
            log.info("매물 추천 요청 완료");
            return ResponseEntity.status(apiResponse.getStatusCode()).body(response);
            
        } catch (CustomException e) {
            throw e;
        } catch (Exception e) {
            log.error("매물 추천 처리 중 예상치 못한 오류 발생", e);
            throw new CustomException(ErrorCode.INTERNAL_SERVER_ERROR, e);
        }
    }

    private List<Double> convertAddressToCoordinates(String address) {
        double[] coords = kakaoCoordinateClient.getCoordinatesByAddress(address);
        if (coords == null) {
            log.warn("주소 좌표 변환 실패: {}", address);
            throw new CustomException(ErrorCode.COORDINATE_CONVERSION_FAILED, "주소로 좌표 변환 실패: " + address);
        }
        
        log.debug("주소 좌표 변환 성공: {} -> ({}, {})", address, coords[LONGITUDE_INDEX], coords[LATITUDE_INDEX]);
        return Arrays.asList(coords[LONGITUDE_INDEX], coords[LATITUDE_INDEX]);
    }

    private Map<String, Object> buildRecommendAreaPayload(RecommendRequest request, List<Double> jobLocationArray) {
        Map<String, Object> payload = new HashMap<>();
        payload.put("age", request.age());
        payload.put("gender", request.gender());
        payload.put("job_location", jobLocationArray);
        payload.put("transportation", request.transportation());
        payload.put("budget", request.budget());
        payload.put("priority", request.priority());
        payload.put("max_commute_min", request.max_commute_min());
        
        log.debug("지역 추천 API 페이로드 생성 완료: {}", payload);
        return payload;
    }

    private ResponseEntity<String> callRecommendAreaApi(Map<String, Object> payload) {
        String fullUrl = recommendApiUrl + RECOMMEND_AREA_ENDPOINT;
        HttpHeaders headers = createJsonHeaders();
        
        log.info("지역 추천 API 호출: {}", fullUrl);
        
        try {
            return restTemplate.exchange(
                    fullUrl,
                    HttpMethod.POST,
                    new HttpEntity<>(payload, headers),
                    String.class
            );
        } catch (Exception e) {
            log.error("지역 추천 API 호출 실패: {}", fullUrl, e);
            throw new CustomException(ErrorCode.RECOMMEND_API_ERROR, e);
        }
    }

    private ResponseEntity<String> callRecommendPropertyApi(RecommendPropertyRequest request) {
        String fullUrl = recommendApiUrl + RECOMMEND_PROPERTY_ENDPOINT;
        HttpHeaders headers = createJsonHeaders();
        
        log.info("매물 추천 API 호출: {}", fullUrl);
        
        try {
            return restTemplate.exchange(
                    fullUrl,
                    HttpMethod.POST,
                    new HttpEntity<>(request, headers),
                    String.class
            );
        } catch (Exception e) {
            log.error("매물 추천 API 호출 실패: {}", fullUrl, e);
            throw new CustomException(ErrorCode.RECOMMEND_API_ERROR, e);
        }
    }

    private HttpHeaders createJsonHeaders() {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        return headers;
    }

    private List<RecommendAreaResponse.Area> parseRecommendedAreas(String responseBody) {
        try {
            JsonNode root = objectMapper.readTree(responseBody);
            JsonNode areaNode = root.get(RECOMMENDED_AREA_FIELD);
            
            if (areaNode != null && areaNode.isArray()) {
                RecommendAreaResponse.Area[] areas = objectMapper.treeToValue(areaNode, RecommendAreaResponse.Area[].class);
                return Arrays.asList(areas);
            } else {
                log.warn("추천 지역 데이터가 없거나 잘못된 형식입니다.");
                return Collections.emptyList();
            }
        } catch (Exception e) {
            log.error("지역 추천 API 응답 파싱 실패", e);
            throw new CustomException(ErrorCode.RECOMMEND_API_ERROR, e);
        }
    }

    private RecommendPropertyResponse parseRecommendPropertyResponse(String responseBody) {
        try {
            return objectMapper.readValue(responseBody, RecommendPropertyResponse.class);
        } catch (Exception e) {
            log.error("매물 추천 API 응답 파싱 실패", e);
            throw new CustomException(ErrorCode.RECOMMEND_API_ERROR, e);
        }
    }
}
