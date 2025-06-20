package com.nomad.seoulbang;

import io.github.cdimascio.dotenv.Dotenv;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.core.env.MapPropertySource;
import org.springframework.core.env.StandardEnvironment;

import java.util.HashMap;
import java.util.Map;

@SpringBootApplication
public class SeoulbangApplication {
    public static void main(String[] args) {
        // 1. .env 파일에서 환경변수 로드
        Dotenv dotenv = Dotenv.configure().ignoreIfMissing().load();

        // 2. Dotenv 내용을 Map으로 변환
        Map<String, Object> env = new HashMap<>();
        dotenv.entries().forEach(entry -> env.put(entry.getKey(), entry.getValue()));

        // 3. Spring에서 사용하는 Environment에 PropertySource 추가
        StandardEnvironment environment = new StandardEnvironment();
        environment.getPropertySources().addLast(
                new MapPropertySource("dotenvProperties", env)
        );

        // 4. SpringApplication에 Custom Environment 적용
        SpringApplication app = new SpringApplication(SeoulbangApplication.class);
        app.setEnvironment(environment);
        app.run(args);
    }
}
