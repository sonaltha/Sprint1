package com.example.Recommend.Repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.example.Recommend.Model.User;

public interface UserRepository extends JpaRepository<User, Integer> {
    User findByEmail(String email);
}
