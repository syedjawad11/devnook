---
title: "What is a REST API in Java? A Complete Guide with Examples"
description: "Learn what a REST API is in Java, how it works, and how to build one using Spring Boot. Includes code examples and common pitfalls to avoid."
published_date: "2026-05-02"
category: "languages"
language: "java"
concept: "rest-api"
template_id: "lang-v1"
tags: ["java", "rest-api", "spring-boot", "web-development", "backend"]
difficulty: "intermediate"
related_posts: []
related_tools: []
og_image: "/og/languages/java/rest-api.png"
---

# What is a REST API in Java? A Complete Guide with Examples

A REST API in Java is the backbone of virtually every modern backend service — from mobile app backends to enterprise microservices — and understanding how to build one correctly is essential for any Java developer working in the web space. For related foundational topics, see [HTTP Status Codes: Complete Reference](/guides/http-status-codes-guide/) and [What is JWT?](/guides/what-is-jwt/) for securing your REST endpoints.

## What is a REST API in Java?

REST, which stands for Representational State Transfer, is an architectural style for designing distributed networked systems. Coined by Roy Fielding in his 2000 doctoral dissertation, REST is not a protocol, a library, or a framework — it is a set of architectural constraints that, when applied to an HTTP-based system, produce a predictable and scalable API.

The six REST constraints are: **client-server separation** (the client and server evolve independently), **statelessness** (each request must contain all information needed to process it — no server-side session), **cacheability** (responses should declare whether they can be cached), **layered system** (intermediaries such as load balancers are transparent to the client), **uniform interface** (resources are identified by URIs, manipulated through representations, and communicate via self-descriptive messages), and **code on demand** (optional: servers may transfer executable code to clients).

In Java, REST APIs are most commonly implemented via two paths. The first is the **JAX-RS specification** — a standard Java EE API with implementations such as Jersey and RESTEasy that map HTTP verbs to annotated Java methods. The second, and by far the more prevalent in modern development, is **Spring MVC / Spring Boot**, which provides opinionated auto-configuration, an embedded Tomcat server, and a rich annotation model (`@RestController`, `@GetMapping`, etc.) that dramatically reduces boilerplate. Java's strong typing, mature concurrency primitives, and vast ecosystem of libraries (Hibernate, Spring Security, Jackson) make it one of the most capable and widely deployed platforms for enterprise-grade REST APIs.

## Why Java Developers Use REST APIs

The predominant driver for REST adoption in Java is the **microservices architecture**. In a microservices system, each independently deployable service exposes a REST interface over HTTP. An order-processing service might expose `POST /orders`, while an inventory service exposes `GET /products/{id}`. These services communicate with each other and with frontend clients through their REST interfaces, enabling teams to deploy, scale, and iterate on individual services without touching the rest of the system.

A second major use case is **mobile and single-page application backends**. An Android application or a React frontend communicates with a Java server through HTTP requests to REST endpoints. The server serialises domain objects to JSON (via Jackson, which Spring Boot auto-configures), and the client deserialises that JSON into its own model. This decoupling means the same Java backend can serve iOS, Android, and web clients simultaneously.

Third, REST enables seamless **third-party integrations**. Payment gateways such as Stripe, CRM platforms such as Salesforce, and messaging providers such as Twilio all expose REST APIs. A Java backend that needs to charge a customer or send a notification will make outbound HTTP calls to these external APIs. The same HTTP semantics that govern public APIs also govern internal service-to-service communication, creating a uniform integration model across the entire system.

Spring Boot's convention-over-configuration approach reduces the time from concept to working REST endpoint to minutes — something that historically required significant XML configuration in legacy Spring MVC setups.

## Basic Syntax

The simplest possible Spring Boot REST controller requires only a class annotation and a method annotation:

```java
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController                       // Marks this class as a REST controller; combines @Controller + @ResponseBody
@RequestMapping("/api")               // Base path prepended to all routes in this class
public class GreetingController {

    @GetMapping("/greet")             // Maps HTTP GET /api/greet to this method
    public String greet() {
        return "Hello, World!";       // Spring Boot's Jackson auto-config serialises this to a plain text response
    }
}
```

`@RestController` is a composed annotation that combines `@Controller` (registers the class as an MVC controller) and `@ResponseBody` (writes the return value directly to the HTTP response body, bypassing view resolution). Because Spring Boot auto-configures Jackson's `ObjectMapper`, returning a `String` produces a `text/plain` response, while returning a POJO produces an `application/json` response with no additional configuration needed. The `@RequestMapping("/api")` on the class acts as a URL prefix, so the effective route is `/api/greet`.

## A Practical Example

The following example demonstrates a more realistic REST controller for a product catalogue service. It shows the three most common endpoint patterns — fetch all resources, fetch one by ID, and create a new resource:

```java
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;

@RestController
@RequestMapping("/api/products")              // All routes in this controller share this base path
public class ProductController {

    // In-memory list standing in for a real repository (illustrative only)
    private final List<Product> products = new ArrayList<>();

    @GetMapping                               // GET /api/products — returns all products as a JSON array
    public ResponseEntity<List<Product>> getAllProducts() {
        return ResponseEntity.ok(products);   // 200 OK with the list serialised to JSON
    }

    @GetMapping("/{id}")                      // GET /api/products/{id} — @PathVariable extracts the ID from the URL
    public ResponseEntity<Product> getProduct(@PathVariable Long id) {
        return products.stream()
            .filter(p -> p.getId().equals(id))
            .findFirst()
            .map(ResponseEntity::ok)          // Found → 200 OK
            .orElse(ResponseEntity.notFound().build()); // Not found → 404 Not Found
    }

    @PostMapping                              // POST /api/products — @RequestBody deserialises the JSON body into a Product
    public ResponseEntity<Product> createProduct(@RequestBody Product product) {
        product.setId((long) (products.size() + 1)); // Assign a simple incremented ID
        products.add(product);
        return ResponseEntity.status(HttpStatus.CREATED).body(product); // 201 Created
    }
}
```

This controller illustrates several important practices. `ResponseEntity<T>` gives the developer explicit control over the HTTP status code — returning `ResponseEntity.ok()` for a successful GET, `ResponseEntity.notFound()` for a missing resource, and `HttpStatus.CREATED` (201) for a successful POST. This matters because clients and API gateways rely on these status codes to determine how to handle responses. `@RequestBody` instructs Spring to pass the raw HTTP request body through Jackson's `ObjectMapper`, converting the incoming JSON payload into a `Product` instance automatically. The stream-based lookup mimics the pattern you would use with a Spring Data repository, where you'd instead call `productRepository.findById(id)`.

## Common Mistakes

**Mistake 1: Violating Statelessness**

A frequent mistake for developers transitioning from servlet-based web apps is storing request context in controller fields or HTTP session objects. For example, maintaining a `currentUser` field on the `@RestController` singleton seems convenient but immediately breaks statelessness — and introduces a race condition since the controller is shared across all threads. The fix is to pass all necessary context in the request itself: use a `Authorization: Bearer <jwt>` header and validate the token per request, or include the user ID in the request body or path. Spring Security's `SecurityContextHolder` provides a thread-local mechanism for accessing the authenticated principal within a single request lifecycle without leaking across requests.

**Mistake 2: Using the Wrong HTTP Method**

Using `POST` for read operations or `GET` to mutate data violates the HTTP specification's safety and idempotency guarantees. `GET` and `HEAD` must be **safe** — they must not modify server state. `PUT`, `DELETE`, and `GET` must be **idempotent** — calling them multiple times must produce the same result as calling them once. Browsers and HTTP intermediaries (CDNs, load balancers) rely on these semantics for caching and retry logic. A `GET` request that deletes a record will be replayed by browser pre-fetch and broken by CDN caching. Map your operations to: `GET` (read), `POST` (create), `PUT`/`PATCH` (update), `DELETE` (remove).

**Mistake 3: Returning 200 for Every Response**

Returning `200 OK` with an `{"error": "not found"}` body is a widespread anti-pattern. It forces clients to parse the body to detect failures, breaking HTTP-native error handling. Use the correct status code: `201 Created` for successful resource creation, `400 Bad Request` for invalid input (e.g., missing required fields), `404 Not Found` for missing resources, `409 Conflict` for duplicate entity violations, and `422 Unprocessable Entity` for semantic validation errors. Spring Boot's `@ControllerAdvice` and `@ExceptionHandler` make it straightforward to map domain exceptions to the correct HTTP status codes globally.

## REST API vs GraphQL

REST and GraphQL solve the same problem — exposing server data to clients over HTTP — but with different philosophies. A REST API exposes **multiple fixed endpoints**, each returning a predetermined data shape. A GraphQL API exposes **a single endpoint** where the client sends a query describing exactly which fields it needs.

| Dimension | REST | GraphQL |
|---|---|---|
| Endpoints | Many (one per resource) | One (`/graphql`) |
| Over-fetching | Common (fixed response shape) | Eliminated (client specifies fields) |
| HTTP caching | Native (GET responses are cacheable) | Difficult (most queries use POST) |
| Java ecosystem | Mature (Spring Boot, JAX-RS) | Growing (Netflix DGS, Spring GraphQL) |

REST is the right default for most Java backends: it integrates naturally with HTTP infrastructure (CDNs, API gateways, load balancers), is well-understood by every HTTP client, and the Java Spring ecosystem provides first-class support. GraphQL earns its place when frontend clients have highly variable data requirements — for instance, a mobile app that needs a compact product card while a desktop app needs the full product detail — and when over-fetching is a measurable performance problem.

## Under the Hood: Performance & Mechanics

When an HTTP request arrives at a Spring Boot application, it passes through the embedded Tomcat (or Jetty/Undertow) container, which allocates a thread from the worker pool and invokes the **DispatcherServlet**. The `DispatcherServlet` queries its `HandlerMapping` to find the controller method that matches the request's path and HTTP method, then delegates to a `HandlerAdapter` (specifically `RequestMappingHandlerAdapter`) to invoke the method. The return value is processed by a **`HttpMessageConverter`** — for JSON responses, this is `MappingJackson2HttpMessageConverter`, which uses Jackson's `ObjectMapper` to serialise the Java object into a JSON byte stream written directly to the response `OutputStream`.

Jackson's serialisation is reflective by default: it inspects the class hierarchy, discovers public getters, and writes each property as a JSON key. This is O(n) relative to the number of fields. For large list responses, this can be significant. Poorly-designed entity graphs with bidirectional JPA relationships cause Jackson to follow each side of the relationship in an infinite loop, producing a `StackOverflowError` at runtime.

Traditional Spring MVC uses a **thread-per-request** model: each concurrent request occupies a Tomcat thread (default pool: 200 threads). Under high concurrency, thread contention and context-switching overhead become bottlenecks. Spring WebFlux (built on Project Reactor and Netty) addresses this with an **event-loop model** that handles thousands of concurrent connections on a small thread pool (typically one thread per CPU core) by suspending I/O-bound operations non-blockingly. The trade-off is a reactive programming model that is more complex to reason about and test.

Authentication cost is a consistent overhead in stateless REST APIs. Validating a JWT on every request involves HMAC signature verification (O(1) but non-trivial CPU cost) and — if claims are fetched from a database — a potential DB round-trip. Mitigating this with in-memory token caching (e.g., Caffeine-backed Spring Security filter) can cut per-request latency significantly under load.

## Advanced Edge Cases

**Edge Case 1: Circular JSON Serialisation with JPA Entities**

A bidirectional JPA relationship between `Order` and `OrderItem` — where `Order` holds a `List<OrderItem>` and each `OrderItem` holds a back-reference to `Order` — causes Jackson to serialise `Order` → `OrderItem` → `Order` → `OrderItem` indefinitely:

```java
@Entity
public class Order {
    @Id Long id;
    @OneToMany(mappedBy = "order")
    List<OrderItem> items; // Jackson serialises each item...
}

@Entity
public class OrderItem {
    @Id Long id;
    @ManyToOne
    Order order; // ...which serialises the order...which serialises the items... → StackOverflowError
}
```

The standard fix is to annotate the parent side with `@JsonManagedReference` and the child side with `@JsonBackReference`. `@JsonBackReference` instructs Jackson to omit that field during serialisation, breaking the cycle. Alternatively, use `@JsonIgnore` on the back-reference field, or — better for complex APIs — use DTOs (Data Transfer Objects) that explicitly model the JSON shape, decoupling the serialisation contract from the persistence model entirely.

**Edge Case 2: Mutable State in a Singleton Controller**

Spring instantiates `@RestController` beans as singletons by default. Storing mutable state in a controller field creates a race condition under concurrent load:

```java
@RestController
@RequestMapping("/api/counter")
public class CounterController {

    private int count = 0; // DANGER: shared mutable state across all threads

    @PostMapping("/increment")
    public int increment() {
        return ++count; // Non-atomic — read-modify-write is not thread-safe
    }
}
```

Under concurrent requests, two threads can read the same value of `count`, both increment it, and write the same result back — losing an increment. The fix is to keep controllers stateless and delegate to a `@Service` bean that manages state with appropriate synchronisation (`AtomicInteger`, `synchronized`, or a database-backed counter). Controllers should contain only request-mapping logic and input validation; business logic and state belong in the service layer.

## Testing REST APIs in Java

Spring Boot's `@WebMvcTest` is the standard approach for unit-testing REST controllers. It loads only the web layer (controllers, filters, `@ControllerAdvice`) without starting a full application context or hitting a database, making tests fast:

```java
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(ProductController.class)    // Loads only ProductController and its web-layer dependencies
class ProductControllerTest {

    @Autowired
    MockMvc mockMvc;                    // Pre-configured MockMvc for performing requests without a live server

    @MockBean
    ProductService productService;      // Replaces the real service bean with a Mockito mock

    @Test
    void getProduct_returnsProductJson() throws Exception {
        Product product = new Product(1L, "Widget", 9.99);
        when(productService.findById(1L)).thenReturn(product); // Stub the service call

        mockMvc.perform(get("/api/products/1"))                 // Simulate GET /api/products/1
            .andExpect(status().isOk())                        // Assert HTTP 200
            .andExpect(jsonPath("$.name").value("Widget"))     // Assert JSON field
            .andExpect(jsonPath("$.price").value(9.99));       // Assert JSON field
    }
}
```

`MockMvc` simulates the full Spring MVC request processing pipeline — including `DispatcherServlet`, argument resolvers, and message converters — without binding to a network port. `@MockBean` creates a Mockito mock and registers it as a Spring bean, replacing the real `ProductService`. For full integration testing against a running server (including the database), consider **RestAssured** with `@SpringBootTest(webEnvironment = RANDOM_PORT)`, which sends real HTTP requests and is better suited to end-to-end contract verification.

## Quick Reference

- REST is an architectural style over HTTP — not a protocol, library, or framework
- Core annotations: `@RestController`, `@GetMapping`, `@PostMapping`, `@PutMapping`, `@DeleteMapping`, `@PatchMapping`, `@RequestBody`, `@PathVariable`, `@RequestParam`
- Always return `ResponseEntity<T>` to control HTTP status codes explicitly
- Each request must be self-contained — no server-side session state
- Map operations to correct HTTP semantics: GET (safe, idempotent), PUT/DELETE (idempotent), POST (neither)
- Use `@WebMvcTest` + `MockMvc` for fast controller unit tests; use RestAssured for integration tests
- Prefer DTOs over JPA entities as controller return types to avoid circular serialisation and over-exposure of persistence details

## Next Steps

After understanding what a REST API in Java is, the logical next step is building a complete project from scratch: a Spring Boot REST tutorial will walk through project initialisation with Spring Initializr, connecting to a PostgreSQL database via Spring Data JPA, and packaging the service as a Docker container. From there, securing your REST API with Spring Security and JSON Web Tokens is essential knowledge for any production service — the Spring Security JWT guide covers token generation, validation filters, and role-based access control. For a broader view of the Java ecosystem, the Java language hub provides guides on related concepts such as Java annotations, dependency injection, and exception handling that underpin everything covered in this introduction to REST APIs in Java.
