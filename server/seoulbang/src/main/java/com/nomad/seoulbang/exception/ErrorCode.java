package com.nomad.seoulbang.exception;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;

@Getter
@RequiredArgsConstructor
public enum ErrorCode {
    // 공통 에러
    INVALID_INPUT_VALUE(HttpStatus.BAD_REQUEST, "유효하지 않은 입력값입니다."),
    INTERNAL_SERVER_ERROR(HttpStatus.INTERNAL_SERVER_ERROR, "서버 내부 오류가 발생했습니다."),
    
    // 매물 관련 에러
    PROPERTY_NOT_FOUND(HttpStatus.NOT_FOUND, "매물을 찾을 수 없습니다."),
    
    // 주소 관련 에러
    ADDRESS_CONVERSION_FAILED(HttpStatus.BAD_REQUEST, "주소 변환에 실패했습니다."),
    COORDINATE_CONVERSION_FAILED(HttpStatus.BAD_REQUEST, "좌표 변환에 실패했습니다."),
    
    // 외부 API 관련 에러
    KAKAO_API_ERROR(HttpStatus.SERVICE_UNAVAILABLE, "카카오 API 호출 중 오류가 발생했습니다."),
    BUILDING_API_ERROR(HttpStatus.SERVICE_UNAVAILABLE, "건물 정보 API 호출 중 오류가 발생했습니다."),
    RECOMMEND_API_ERROR(HttpStatus.SERVICE_UNAVAILABLE, "추천 API 호출 중 오류가 발생했습니다.");
    
    private final HttpStatus httpStatus;
    private final String message;
} 