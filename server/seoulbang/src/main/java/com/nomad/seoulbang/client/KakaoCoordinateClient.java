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
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

@Service
@Slf4j
public class KakaoCoordinateClient {

    @Value("${kakao.api.key2}")
    private String kakaoApiKey;

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    public KakaoCoordinateClient(RestTemplate restTemplate, ObjectMapper objectMapper) {
        this.restTemplate = restTemplate;
        this.objectMapper = objectMapper;
    }

    @Cacheable(
            value = "kakaoCoordinateCache",
            key = "#address",
            unless = "#result == null"
    )
    public double[] getCoordinatesByAddress(String address) {
        try {
            String url = "https://dapi.kakao.com/v2/local/search/address.json?query=" +
                    URLEncoder.encode(address, StandardCharsets.UTF_8);
            log.info("Kakao 주소→좌표 API 호출: {}", url);

            HttpHeaders headers = new HttpHeaders();
            headers.set("Authorization", "KakaoAK " + kakaoApiKey);
            HttpEntity<String> entity = new HttpEntity<>(headers);

            ResponseEntity<String> response = restTemplate.exchange(
                    URI.create(url), HttpMethod.GET, entity, String.class);

            JsonNode root = objectMapper.readTree(response.getBody());
            JsonNode documents = root.get("documents");

            if (documents != null && documents.isArray() && !documents.isEmpty()) {
                JsonNode first = documents.get(0);
                double longitude = first.get("x").asDouble();
                double latitude = first.get("y").asDouble();
                return new double[]{longitude, latitude};
            }
        } catch (Exception e) {
            log.error("Kakao 주소→좌표 변환 실패", e);
        }
        return null;
    }
}
