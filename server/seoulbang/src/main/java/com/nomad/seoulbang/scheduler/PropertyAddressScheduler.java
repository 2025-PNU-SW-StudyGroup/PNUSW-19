package com.nomad.seoulbang.scheduler;

import com.nomad.seoulbang.service.PropertyAddressService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
@Slf4j
public class PropertyAddressScheduler {
    private final PropertyAddressService propertyAddressService;

    // 하루마다 실행
    @Scheduled(cron = "0 0 5 * * *")
    public void updatePropertyAddresses() {
        log.info("주소 정보 업데이트 스케줄러 실행");
        try {
            propertyAddressService.batchUpdateMissingAddresses();
        } catch (Exception e) {
            log.error("주소 정보 업데이트 스케줄러 오류", e);
        }
    }
}
