package com.nomad.seoulbang.client;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.net.URI;
import java.util.HashMap;
import java.util.Map;

@Service
@Slf4j
public class KakaoAddressClient {

    @Value("${kakao.api.key}")
    private String kakaoApiKey;

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    public KakaoAddressClient(RestTemplate restTemplate, ObjectMapper objectMapper) {
        this.restTemplate = restTemplate;
        this.objectMapper = objectMapper;
    }

    @Cacheable(
            value = "kakaoAddressCache",
            key = "#longitude + '-' + #latitude",
            unless = "#result == null || #result.isEmpty()"
    )
    public Map<String, String> getAddressByCoordinates(double longitude, double latitude) {
        log.info("캐시 미스 - Kakao Address API 호출: {}-{}", longitude, latitude);
        String url = "https://dapi.kakao.com/v2/local/geo/coord2address.json?x=" + longitude + "&y=" + latitude;
        log.info("Kakao 주소 API: {}", url);

        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", "KakaoAK " + kakaoApiKey);
        HttpEntity<String> entity = new HttpEntity<>(headers);

        ResponseEntity<String> response = restTemplate.exchange(URI.create(url), HttpMethod.GET, entity, String.class);
        Map<String, String> addressInfo = new HashMap<>();

        try {
            log.info("Kakao 주소 API 응답: {}", response.getBody());
            JsonNode root = objectMapper.readTree(response.getBody());
            JsonNode documents = root.get("documents");

            if (documents != null && documents.isArray() && !documents.isEmpty()) {
                JsonNode firstDocument = documents.get(0);

                // 지번 주소 (address)
                JsonNode address = firstDocument.get("address");
                if (address != null && address.has("address_name") && !address.get("address_name").isNull()) {
                    String lotNumber = address.get("address_name").asText();
                    addressInfo.put("lotNumber", lotNumber);
                }

                // 도로명 주소 (road_address)
                JsonNode roadAddress = firstDocument.get("road_address");
                if (roadAddress != null && roadAddress.has("address_name") && !roadAddress.get("address_name").isNull()) {
                    String roadAddressName = roadAddress.get("address_name").asText();
                    addressInfo.put("address", roadAddressName);
                }
            }
        } catch (Exception e) {
            log.error("Kakao 주소 API 응답 파싱 오류", e);
        }

        return addressInfo;
    }
}
