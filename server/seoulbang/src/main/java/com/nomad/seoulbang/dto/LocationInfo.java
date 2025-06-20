package com.nomad.seoulbang.dto;

public record LocationInfo(
        String sigunguCd,
        String bjdongCd,
        String bun,
        String ji
) {
    public boolean isValid() {
        return sigunguCd != null && bjdongCd != null && bun != null && ji != null;
    }
}
