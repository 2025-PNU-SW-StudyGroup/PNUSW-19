package com.nomad.seoulbang.service;

import com.nomad.seoulbang.dto.PropertyDetailResponse;
import com.nomad.seoulbang.repository.PropertyRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class PropertyService {
    private final PropertyRepository propertyRepository;

    public PropertyDetailResponse getPropertyDetail(Long propertyId) {
        return propertyRepository.findPropertyDetail(propertyId);
    }
}
