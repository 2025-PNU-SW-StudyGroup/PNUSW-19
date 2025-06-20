package com.nomad.seoulbang.dto;

import java.time.LocalDate;

public record BuildingInfo(
        int parkingSpaces,
        int elevatorCount,
        int hhldCnt,
        int fmlyCnt,
        String mainPurpsCdNm,
        String etcPurps,
        String strctCdNm,
        LocalDate useAprDay
){}
