package com.example.Recommend.Controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import com.example.Recommend.Model.User;
import com.example.Recommend.Repository.UserRepository;

import java.util.*;
@RestController
@RequestMapping("/auth")
@CrossOrigin
public class AuthController {

    @Autowired
    private UserRepository repo;

    @PostMapping("/register")
    public String register(@RequestBody User user) {

        if (repo.findByEmail(user.getEmail()) != null) {
            return "User already exists";
        }

        user.setRole("USER");
        repo.save(user);

        return "Registered successfully";
    }

    @PostMapping("/login")
    public Map<String, String> login(@RequestBody User user) {

        Map<String, String> res = new HashMap<>();
        User existing = repo.findByEmail(user.getEmail());

        if (existing == null) {
            res.put("msg", "User not found");
            return res;
        }

        if (!existing.getPassword().equals(user.getPassword())) {
            res.put("msg", "Wrong password");
            return res;
        }

        res.put("msg", "Login successful");
        res.put("role", existing.getRole());

        return res;
    }
}