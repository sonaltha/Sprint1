package com.example.Recommend.Controller;


import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

@RestController
@CrossOrigin
@RequestMapping("/recommend")
public class RecommendationController {

    @GetMapping("/{movie}")
    public String recommend(@PathVariable String movie) {

        String url = "http://127.0.0.1:8000/recommend/" + movie;

        RestTemplate restTemplate = new RestTemplate();
        return restTemplate.getForObject(url, String.class);
    }
}