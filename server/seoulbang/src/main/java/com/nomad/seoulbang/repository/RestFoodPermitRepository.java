package com.nomad.seoulbang.repository;

import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
@RequiredArgsConstructor
public class RestFoodPermitRepository {

    private final JdbcTemplate jdbcTemplate;

    public void mapNearbyProperty(Long propertyId) {

        String sql = """
            INSERT INTO public.property_rest_food_permit_map (property_id, rest_food_permit_id, distance_meters)
            SELECT p.id, r.id, ST_Distance(p.location::geography, r.location::geography) AS distance_meters
            FROM public.property p
            JOIN public.rest_food_permit r 
            ON r.location && ST_Expand(p.location, 0.01) 
              AND ST_DWithin(p.location::geography, r.location::geography, 1000)
            WHERE p.id = ?
              AND NOT EXISTS (
                  SELECT 1 FROM public.property_rest_food_permit_map m
                  WHERE m.property_id = p.id AND m.rest_food_permit_id = r.id
              )
        """;
        jdbcTemplate.update(sql, propertyId);
    }
}
