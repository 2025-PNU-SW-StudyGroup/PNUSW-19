package com.nomad.seoulbang.repository;

import com.nomad.seoulbang.dto.PropertyDetailResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;

@Repository
@RequiredArgsConstructor
public class PropertyRepository {
    private final JdbcTemplate jdbcTemplate;

    public void batchUpdateAddress(List<Object[]> params, int batchSize) {
        String sql = "UPDATE property SET address = ?, updated_at = NOW() WHERE id = ?";
        jdbcTemplate.batchUpdate(sql, params, batchSize, (PreparedStatement ps, Object[] param) -> {
            ps.setString(1, (String) param[0]);
            ps.setLong(2, (Long) param[1]);
        });
    }

    public void batchUpdateLotNumber(List<Object[]> params, int batchSize) {
        String sql = "UPDATE property SET lot_number = ?, updated_at = NOW() WHERE id = ?";
        jdbcTemplate.batchUpdate(sql, params, batchSize, (PreparedStatement ps, Object[] param) -> {
            ps.setString(1, (String) param[0]);
            ps.setLong(2, (Long) param[1]);
        });
    }

    public void batchUpdateAddressAndLotNumber(List<Object[]> params, int batchSize) {
        String sql = "UPDATE property SET address = ?, lot_number = ?, updated_at = NOW() WHERE id = ?";
        jdbcTemplate.batchUpdate(sql, params, batchSize, (PreparedStatement ps, Object[] param) -> {
            ps.setString(1, (String) param[0]);
            ps.setString(2, (String) param[1]);
            ps.setLong(3, (Long) param[2]);
        });
    }

    public List<Map<String, Object>> findPropertiesBasicInfo() {
        String sql = """
        SELECT id, ST_X("location") AS lon, ST_Y("location") AS lat, address, lot_number
        FROM property
        WHERE location IS NOT NULL AND (
            lot_number IS NULL OR lot_number = ''
        )
        """;
        return jdbcTemplate.queryForList(sql);
    }

    public void updatePropertyInfo(
            long id,
            int parkingSpaces,
            int elevatorCount,
            int hhldCnt,
            int fmlyCnt,
            String mainPurpsCdNm,
            String etcPurps,
            String strctCdNm,
            LocalDate useAprDay
    ) {
        String sql = """
            UPDATE property
            SET parking_spaces = ?, 
                elevator_count = ?, 
                household_count = ?, 
                family_count = ?, 
                main_purpose = ?, 
                etc_purpose = ?, 
                structure_code = ?, 
                approval_date = ?, 
                updated_at = NOW(),
                is_checked = TRUE
            WHERE id = ?
        """;
        jdbcTemplate.update(sql, parkingSpaces, elevatorCount, hhldCnt, fmlyCnt, mainPurpsCdNm, etcPurps, strctCdNm, useAprDay, id);
    }

    public List<Map<String, Object>> findPropertiesWithMissingInfo(int batchSize) {
        String sql = """
            SELECT id, administrative_code, lot_number
            FROM property
            WHERE is_checked IS NOT TRUE
            LIMIT ?
        """;
        return jdbcTemplate.queryForList(sql, batchSize);
    }

    public List<Map<String, Object>> findPropertiesMissingResidentialArea(int limit) {
        String sql = """
            SELECT id, ST_X("location") AS lon, ST_Y("location") AS lat
            FROM property
            WHERE residential_area IS NULL
            ORDER BY created_at DESC
            LIMIT ?
        """;
        return jdbcTemplate.queryForList(sql, limit);
    }

    // 공간조인으로 주거전용지역명 조회
    public String findResidentialArea(double lon, double lat) {
        String sql = """
            SELECT "DGM_NM"
            FROM "UPIS_C_UQ111"
            WHERE ST_Contains(geom, ST_SetSRID(ST_MakePoint(?, ?), 4326))
            LIMIT 1
        """;
        List<String> result = jdbcTemplate.queryForList(sql, String.class, lon, lat);
        return result.isEmpty() ? null : result.get(0);
    }

    public void batchUpdateResidentialArea(List<Object[]> params) {
        String sql = """
            UPDATE property
            SET residential_area = ?, updated_at = NOW()
            WHERE id = ?
        """;
        jdbcTemplate.batchUpdate(sql, params);
    }

    // 음식점 인허가 매핑 안된 매물 조회
    public List<Long> findUnmappedForRestFoodPermit() {
        String sql = """
            SELECT p.id
            FROM public.property p
            WHERE NOT EXISTS (
                SELECT 1 FROM public.property_rest_food_permit_map m
                WHERE m.property_id = p.id
            )
        """;
        return jdbcTemplate.queryForList(sql, Long.class);
    }

    // 버스정류장 매핑 안된 매물 조회
    public List<Long> findUnmappedForBusStop() {
        String sql = """
            SELECT p.id
            FROM public.property p
            WHERE NOT EXISTS (
                SELECT 1 FROM public.property_bus_stop_map m
                WHERE m.property_id = p.id
            )
        """;
        return jdbcTemplate.queryForList(sql, Long.class);
    }

    // CCTV 매핑 안된 매물 조회
    public List<Long> findUnmappedForCctv() {
        String sql = """
            SELECT p.id
            FROM public.property p
            WHERE NOT EXISTS (
                SELECT 1 FROM public.property_cctv_map m
                WHERE m.property_id = p.id
            )
        """;
        return jdbcTemplate.queryForList(sql, Long.class);
    }

    // 지하철역 매핑 안된 매물 조회
    public List<Long> findUnmappedForSubway() {
        String sql = """
            SELECT p.id
            FROM public.property p
            WHERE NOT EXISTS (
                SELECT 1 FROM public.property_subway_map m
                WHERE m.property_id = p.id
            )
        """;
        return jdbcTemplate.queryForList(sql, Long.class);
    }

    public PropertyDetailResponse findPropertyDetail(Long propertyId) {
        // 1. property 기본 정보
        String propertySql = "" +
                "SELECT ST_X(location) AS longitude, ST_Y(location) AS latitude, * FROM property WHERE id = ?";
        PropertyDetailResponse property = jdbcTemplate.queryForObject(propertySql, (rs, rowNum) -> mapProperty(rs), propertyId);

        // 2. 사진
        String photoSql = "SELECT image_url, image_type, \"order\" FROM property_photo WHERE property_id = ? ORDER BY \"order\" ASC";
        List<PropertyDetailResponse.Photo> photos = jdbcTemplate.query(photoSql,
                (rs, rowNum) -> new PropertyDetailResponse.Photo(
                        rs.getString("image_url"),
                        rs.getString("image_type"),
                        rs.getObject("order") != null ? rs.getInt("order") : null
                ), propertyId);

        // 3. 태그
        String tagSql = "SELECT name FROM property_tag WHERE property_id = ?";
        List<String> tags = jdbcTemplate.query(tagSql, (rs, rowNum) -> rs.getString("name"), propertyId);

        // 4. 주변 시설 상세 정보 (조인)
        List<PropertyDetailResponse.BusStop> busStops = jdbcTemplate.query("""
            SELECT m.bus_stop_id AS id, m.distance_meters, 
                   b.stop_name, b.stop_type, b.stop_number, b.latitude, b.longitude, b.bus_arrival_info_display_installed
            FROM property_bus_stop_map m
            JOIN bus_stop b ON m.bus_stop_id = b.id
            WHERE m.property_id = ?
            ORDER BY m.distance_meters ASC
        """, (rs, rowNum) -> new PropertyDetailResponse.BusStop(
                rs.getLong("id"),
                rs.getDouble("distance_meters"),
                rs.getString("stop_name"),
                rs.getString("stop_type"),
                rs.getObject("stop_number") != null ? rs.getInt("stop_number") : null,
                rs.getObject("latitude") != null ? rs.getDouble("latitude") : null,
                rs.getObject("longitude") != null ? rs.getDouble("longitude") : null,
                rs.getString("bus_arrival_info_display_installed")
        ), propertyId);

        List<PropertyDetailResponse.Subway> subways = jdbcTemplate.query("""
            SELECT m.subway_id AS id, m.distance_meters,
                   s.sequence_number, s.line_number, s.unique_station_code, s.station_name,
                   s.latitude, s.longitude
            FROM property_subway_map m
            JOIN subway s ON m.subway_id = s.id
            WHERE m.property_id = ?
            ORDER BY m.distance_meters ASC
        """, (rs, rowNum) -> new PropertyDetailResponse.Subway(
                rs.getLong("id"),
                rs.getDouble("distance_meters"),
                rs.getString("sequence_number"),
                rs.getString("line_number"),
                rs.getString("unique_station_code"),
                rs.getString("station_name"),
                parseDoubleSafe(rs.getString("latitude")),
                parseDoubleSafe(rs.getString("longitude"))
        ), propertyId);

        List<PropertyDetailResponse.Cctv> cctvs = jdbcTemplate.query("""
            SELECT m.cctv_id AS id, m.distance_meters,
                   c.region, c.safe_address, c.latitude, c.longitude, c.cctv_count, c.modified_datetime
            FROM property_cctv_map m
            JOIN cctv c ON m.cctv_id = c.id
            WHERE m.property_id = ?
            ORDER BY m.distance_meters ASC
        """, (rs, rowNum) -> new PropertyDetailResponse.Cctv(
                rs.getLong("id"),
                rs.getDouble("distance_meters"),
                rs.getString("region"),
                rs.getString("safe_address"),
                rs.getObject("latitude") != null ? rs.getDouble("latitude") : null,
                rs.getObject("longitude") != null ? rs.getDouble("longitude") : null,
                rs.getObject("cctv_count") != null ? rs.getInt("cctv_count") : null,
                rs.getString("modified_datetime")
        ), propertyId);

        List<PropertyDetailResponse.RestFoodPermit> restFoodPermits = jdbcTemplate.query("""
            SELECT m.rest_food_permit_id AS id, m.distance_meters,
                   r.bplcnm, r.sitewhladdr, r.rdnwhladdr, r.uptaenm, r.mgtno, r.opnsfteamcode,
                   r.sitearea, r.sitetel, r.x, r.y
            FROM property_rest_food_permit_map m
            JOIN rest_food_permit r ON m.rest_food_permit_id = r.id
            WHERE m.property_id = ?
            ORDER BY m.distance_meters ASC
        """, (rs, rowNum) -> new PropertyDetailResponse.RestFoodPermit(
                rs.getLong("id"),
                rs.getDouble("distance_meters"),
                rs.getString("bplcnm"),
                rs.getString("sitewhladdr"),
                rs.getString("rdnwhladdr"),
                rs.getString("uptaenm"),
                rs.getString("mgtno"),
                rs.getString("opnsfteamcode"),
                rs.getString("sitearea"),
                rs.getString("sitetel"),
                parseDoubleSafe(rs.getString("x")),
                parseDoubleSafe(rs.getString("y"))
        ), propertyId);

        // 5. 응답 조립
        return new PropertyDetailResponse(
                property.propertyId(), property.address(), property.longitude(), property.latitude(), property.deposit(), property.monthlyRentCost(),
                property.maintenanceCost(), property.area(), property.floor(), property.propertyType(),
                property.features(), property.direction(), property.residentialArea(), property.lotNumber(),
                property.description(), property.agentName(), property.agentOffice(), property.agentPhone(),
                property.agentAddress(), property.agentRegistrationNo(), property.propertyNumber(),
                property.administrativeCode(), property.propertyName(), property.transactionType(),
                property.confirmationType(), property.supplyArea(), property.propertyConfirmationDate(),
                property.mainImageUrl(), property.roomsBathrooms(), property.duplex(), property.availableMoveInDate(),
                property.parkingSpaces(), property.totalFloor(), property.roomType(), property.elevatorCount(),
                property.householdCount(), property.familyCount(), property.mainPurpose(), property.etcPurpose(),
                property.structureCode(), property.approvalDate(),
                photos, tags, busStops, subways, cctvs, restFoodPermits
        );
    }

    private static Double parseDoubleSafe(String value) {
        try {
            return value == null ? null : Double.parseDouble(value);
        } catch (Exception e) {
            return null;
        }
    }

    private PropertyDetailResponse mapProperty(ResultSet rs) throws SQLException {
        return new PropertyDetailResponse(
                rs.getLong("id"),
                rs.getString("address"),
                rs.getObject("longitude") != null ? rs.getDouble("longitude") : null,
                rs.getObject("latitude") != null ? rs.getDouble("latitude") : null,
                rs.getObject("deposit") != null ? rs.getLong("deposit") : null,
                rs.getObject("monthly_rent_cost") != null ? rs.getLong("monthly_rent_cost") : null,
                rs.getObject("maintenance_cost") != null ? rs.getLong("maintenance_cost") : null,
                rs.getObject("area") != null ? rs.getDouble("area") : null,
                rs.getObject("floor") != null ? rs.getInt("floor") : null,
                rs.getString("property_type"),
                rs.getString("features"),
                rs.getString("direction"),
                rs.getString("residential_area"),
                rs.getString("lot_number"),
                rs.getString("description"),
                rs.getString("agent_name"),
                rs.getString("agent_office"),
                rs.getString("agent_phone"),
                rs.getString("agent_address"),
                rs.getString("agent_registration_no"),
                rs.getString("property_number"),
                rs.getString("administrative_code"),
                rs.getString("property_name"),
                rs.getString("transaction_type"),
                rs.getString("confirmation_type"),
                rs.getObject("supply_area") != null ? ((Number)rs.getObject("supply_area")).doubleValue() : null,
                rs.getObject("property_confirmation_date") != null ? rs.getObject("property_confirmation_date", LocalDate.class) : null,
                rs.getString("main_image_url"),
                rs.getString("rooms_bathrooms"),
                rs.getObject("duplex") != null ? rs.getBoolean("duplex") : null,
                rs.getString("available_move_in_date"),
                rs.getObject("parking_spaces") != null ? rs.getInt("parking_spaces") : null,
                rs.getObject("total_floor") != null ? rs.getInt("total_floor") : null,
                rs.getString("room_type"),
                rs.getObject("elevator_count") != null ? rs.getInt("elevator_count") : null,
                rs.getObject("household_count") != null ? rs.getInt("household_count") : null,
                rs.getObject("family_count") != null ? rs.getInt("family_count") : null,
                rs.getString("main_purpose"),
                rs.getString("etc_purpose"),
                rs.getString("structure_code"),
                rs.getObject("approval_date") != null ? rs.getObject("approval_date", LocalDate.class) : null,
                null, null, null, null, null, null // photos, tags, busStops, subways, cctvs, restFoodPermits
        );
    }
}
