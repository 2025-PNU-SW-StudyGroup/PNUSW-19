package com.nomad.seoulbang.scheduler;

import com.nomad.seoulbang.repository.PropertyRepository;
import com.nomad.seoulbang.service.BuildingInfoService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;

@Component
@RequiredArgsConstructor
@Slf4j
public class BuildingInfoScheduler {
    private final BuildingInfoService buildingInfoService;
    private final PropertyRepository propertyRepository;

    // 매일 새벽 3시 건물 정보 업데이트 실행
    @Scheduled(cron = "0 0 3 * * *")
    public void updateMissingBuildingInfo() {
        log.info("[스케줄러] 건물 정보 업데이트 시작");
        try {
            // 1. DB에서 업데이트가 필요한 건물 정보 목록 가져오기
            List<Map<String, Object>> buildingsToUpdate = propertyRepository.findPropertiesWithMissingInfo(50);

            // 2. 각 건물 정보에 대해 업데이트 처리
            for (Map<String, Object> building : buildingsToUpdate) {
                buildingInfoService.updateBuildingInfo(building);
            }

            log.info("[스케줄러] 건물 정보 업데이트 완료");
        } catch (Exception e) {
            log.error("[스케줄러] 건물 정보 업데이트 중 오류 발생", e);
        }
    }
}
