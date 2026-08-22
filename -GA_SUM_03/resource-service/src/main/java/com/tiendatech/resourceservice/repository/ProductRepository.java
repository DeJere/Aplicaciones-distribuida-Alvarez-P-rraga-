package com.tiendatech.resourceservice.repository;

import com.tiendatech.resourceservice.model.Product;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProductRepository extends JpaRepository<Product, Long> {
}
