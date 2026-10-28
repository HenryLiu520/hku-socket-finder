package hku.sf.web;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class ApiExceptionHandler {

    @ExceptionHandler(ApiException.class)
    public ResponseEntity<Dtos.ApiError> handle(ApiException e) {
        return ResponseEntity.status(e.status).body(new Dtos.ApiError(e.code, e.getMessage()));
    }
}
