package com.nomad.seoulbang.client;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.net.URI;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

@Component
@Slf4j
@RequiredArgsConstructor
public class BuildingApiClient {

    @Value("${public.api.key}")
    private String apiKey;
    private final String BASE_URL = "http://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo";

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    public JsonNode getBuildingInfo(String sigunguCd, String bjdongCd, String bun, String ji) {
        String url = buildApiUrl(sigunguCd, bjdongCd, bun, ji);
        log.info("URL: {}, bun: {}, ji: {}", url, bun, ji);

        try {
            ResponseEntity<String> response = callApi(url);
            return parseResponse(response.getBody());
        } catch (Exception e) {
            log.error("건물 정보 API 호출 실패", e);
            return objectMapper.createArrayNode();
        }
    }

    private String buildApiUrl(String sigunguCd, String bjdongCd, String bun, String ji) {
        return String.format("%s?serviceKey=%s&sigunguCd=%s&bjdongCd=%s&bun=%s&ji=%s&_type=json",
                BASE_URL, apiKey, encode(sigunguCd), encode(bjdongCd), encode(bun), encode(ji));
    }

    private String encode(String value) {
        return URLEncoder.encode(value, StandardCharsets.UTF_8);
    }

    private ResponseEntity<String> callApi(String url) {
        return restTemplate.getForEntity(URI.create(url), String.class);
    }

    private JsonNode parseResponse(String responseBody) throws Exception {
        log.info("API 응답 내용: {}", responseBody);
        JsonNode root = objectMapper.readTree(responseBody);
        return root.path("response").path("body").path("items").path("item");
    }
}
