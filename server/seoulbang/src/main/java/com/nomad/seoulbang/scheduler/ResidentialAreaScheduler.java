package com.nomad.seoulbang.scheduler;

import com.nomad.seoulbang.service.PropertyResidentialAreaService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
@Slf4j
public class ResidentialAreaScheduler {
    private final PropertyResidentialAreaService propertyResidentialAreasUpdateService;

    public ResidentialAreaScheduler(PropertyResidentialAreaService propertyResidentialAreasUpdateService) {
        this.propertyResidentialAreasUpdateService = propertyResidentialAreasUpdateService;
    }

    // 하루마다 실행
    @Scheduled(cron = "0 0 6 * * *")
    public void updateResidentialAreas() {
        log.info("주거전용지역 일괄 업데이트 스케줄러 실행");
        try {
            propertyResidentialAreasUpdateService.updateResidentialAreasForNewProperties();
        } catch (Exception e) {
            log.error("주거전용지역 업데이트 스케줄러 오류", e);
        }
    }
}
