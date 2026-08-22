package com.tiendatech.resourceservice.service;

import com.tiendatech.resourceservice.client.NotificationClient;
import com.tiendatech.resourceservice.model.Product;
import com.tiendatech.resourceservice.repository.ProductRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class ProductService {

    private final ProductRepository productRepository;
    private final NotificationClient notificationClient;

    public ProductService(ProductRepository productRepository, NotificationClient notificationClient) {
        this.productRepository = productRepository;
        this.notificationClient = notificationClient;
    }

    public List<Product> getAllProducts() {
        return productRepository.findAll();
    }

    public Optional<Product> getProductById(Long id) {
        return productRepository.findById(id);
    }

    public Product createProduct(Product product) {
        Product saved = productRepository.save(product);
        notificationClient.notify(saved.getId(), "PRODUCT_CREATED",
                "Producto creado: " + saved.getName());
        return saved;
    }

    public Product updateProduct(Long id, Product productDetails) {
        return productRepository.findById(id)
                .map(product -> {
                    product.setName(productDetails.getName());
                    product.setDescription(productDetails.getDescription());
                    product.setPrice(productDetails.getPrice());
                    product.setStock(productDetails.getStock());
                    product.setCategory(productDetails.getCategory());
                    Product updated = productRepository.save(product);
                    notificationClient.notify(updated.getId(), "PRODUCT_UPDATED",
                            "Producto actualizado: " + updated.getName());
                    return updated;
                })
                .orElseThrow(() -> new RuntimeException("Producto no encontrado: " + id));
    }

    public void deleteProduct(Long id) {
        if (productRepository.existsById(id)) {
            productRepository.deleteById(id);
            notificationClient.notify(id, "PRODUCT_DELETED",
                    "Producto eliminado con ID: " + id);
        } else {
            throw new RuntimeException("Producto no encontrado: " + id);
        }
    }
}
