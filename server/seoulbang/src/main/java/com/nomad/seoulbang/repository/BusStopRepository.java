package com.nomad.seoulbang.repository;

import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
@RequiredArgsConstructor
public class BusStopRepository {

    private final JdbcTemplate jdbcTemplate;

    public void mapNearbyProperty(Long propertyId) {
        String sql = """
            INSERT INTO public.property_bus_stop_map (property_id, bus_stop_id, distance_meters)
            SELECT p.id, b.id, ST_Distance(p.location::geography, b.location::geography) AS distance_meters
            FROM public.property p
            JOIN public.bus_stop b
              ON b.location && ST_Expand(p.location, 0.01)
             AND ST_DWithin(p.location::geography, b.location::geography, 1000)
            WHERE p.id = ?
              AND NOT EXISTS (
                  SELECT 1 FROM public.property_bus_stop_map m
                  WHERE m.property_id = p.id AND m.bus_stop_id = b.id
              )
        """;
        jdbcTemplate.update(sql, propertyId);
    }
}


