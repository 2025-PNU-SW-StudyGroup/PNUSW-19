package com.nomad.seoulbang.scheduler;

import com.nomad.seoulbang.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
@RequiredArgsConstructor
public class FacilityMappingScheduler {

    private final PropertyRepository propertyRepository;
    private final RestFoodPermitRepository restFoodPermitRepository;
    private final BusStopRepository busStopRepository;
    private final CctvRepository cctvRepository;
    private final SubwayRepository subwayRepository;

    // 음식점 인허가 매핑
    @Scheduled(cron = "0 0 4 * * *")
    public void scheduledRestFoodPermitMapping() {
        List<Long> unmappedPropertyIds = propertyRepository.findUnmappedForRestFoodPermit();
        for (Long propertyId : unmappedPropertyIds) {
            restFoodPermitRepository.mapNearbyProperty(propertyId);
        }
    }

    // 버스정류장 매핑
    @Scheduled(cron = "0 10 4 * * *")
    public void scheduledBusStopMapping() {
        List<Long> unmappedPropertyIds = propertyRepository.findUnmappedForBusStop();
        for (Long propertyId : unmappedPropertyIds) {
            busStopRepository.mapNearbyProperty(propertyId);
        }
    }

    // CCTV 매핑
    @Scheduled(cron = "0 20 4 * * *")
    public void scheduledCctvMapping() {
        List<Long> unmappedPropertyIds = propertyRepository.findUnmappedForCctv();
        for (Long propertyId : unmappedPropertyIds) {
            cctvRepository.mapNearbyProperty(propertyId);
        }
    }

    // 지하철역 매핑
    @Scheduled(cron = "0 30 4 * * *")
    public void scheduledSubwayMapping() {
        List<Long> unmappedPropertyIds = propertyRepository.findUnmappedForSubway();
        for (Long propertyId : unmappedPropertyIds) {
            subwayRepository.mapNearbyProperty(propertyId);
        }
    }
}