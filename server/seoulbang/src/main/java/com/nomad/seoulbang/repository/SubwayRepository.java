package com.nomad.seoulbang.repository;

import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
@RequiredArgsConstructor
public class SubwayRepository {

    private final JdbcTemplate jdbcTemplate;

    public void mapNearbyProperty(Long propertyId) {
        String sql = """
            INSERT INTO public.property_subway_map (property_id, subway_id, distance_meters)
            SELECT p.id, s.id, ST_Distance(p.location::geography, s.location::geography) AS distance_meters
            FROM public.property p
            JOIN public.subway s
              ON s.location && ST_Expand(p.location, 0.01)
             AND ST_DWithin(p.location::geography, s.location::geography, 1000)
            WHERE p.id = ?
              AND NOT EXISTS (
                  SELECT 1 FROM public.property_subway_map m
                  WHERE m.property_id = p.id AND m.subway_id = s.id
              )
        """;
        jdbcTemplate.update(sql, propertyId);
    }
}

