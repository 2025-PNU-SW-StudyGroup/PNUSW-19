package com.nomad.seoulbang.util;

public class LotNumberParser {
    public static String extractBun(String lotNumber) {
        // "서울 광진구 광장동 256-1" -> "0256"
        if (lotNumber == null) return null;
        String[] parts = lotNumber.trim().split(" ");
        String bunPart = parts[parts.length - 1].split("-")[0];
        try {
            return String.format("%04d", Integer.parseInt(bunPart));
        } catch (Exception e) {
            return null;
        }
    }

    public static String extractJi(String lotNumber) {
        // "서울 광진구 광장동 256-1" -> "0001"
        if (lotNumber == null) return null;
        String[] parts = lotNumber.trim().split(" ");
        String[] bunJi = parts[parts.length - 1].split("-");
        if (bunJi.length > 1) {
            try {
                return String.format("%04d", Integer.parseInt(bunJi[1]));
            } catch (Exception e) {
                return "0000";
            }
        } else {
            return "0000";
        }
    }

}