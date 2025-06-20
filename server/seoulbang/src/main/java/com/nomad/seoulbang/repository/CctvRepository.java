package com.nomad.seoulbang.repository;

import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
@RequiredArgsConstructor
public class CctvRepository {
    private final JdbcTemplate jdbcTemplate;

    public void mapNearbyProperty(Long propertyId) {
        String sql = """
            INSERT INTO public.property_cctv_map (property_id, cctv_id, distance_meters)
            SELECT p.id, c.id, ST_Distance(p.location::geography, c.location::geography) AS distance_meters
            FROM public.property p
            JOIN public.cctv c
              ON c.location && ST_Expand(p.location, 0.01)
             AND ST_DWithin(p.location::geography, c.location::geography, 1000)
            WHERE p.id = ?
              AND NOT EXISTS (
                  SELECT 1 FROM public.property_cctv_map m
                  WHERE m.property_id = p.id AND m.cctv_id = c.id
              )
        """;
        jdbcTemplate.update(sql, propertyId);
    }
}

