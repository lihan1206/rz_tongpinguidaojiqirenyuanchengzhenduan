package com.tongping.robot.exception.handler;

import com.tongping.robot.dto.response.ApiResponse;
import com.tongping.robot.exception.BusinessException;
import com.tongping.robot.exception.ErrorCode;
import com.tongping.robot.exception.ResourceNotFoundException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.BindException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.context.request.WebRequest;

import jakarta.servlet.http.HttpServletRequest;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.when;

/**
 * 全局异常处理器单元测试
 */
@DisplayName("全局异常处理器测试")
class GlobalExceptionHandlerTest {

    private GlobalExceptionHandler exceptionHandler;

    @Mock
    private HttpServletRequest request;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        exceptionHandler = new GlobalExceptionHandler();
        when(request.getRequestURI()).thenReturn("/api/v1/test");
    }

    @Test
    @DisplayName("处理业务异常")
    void handleBusinessException_ShouldReturnBadRequest() {
        // Given
        BusinessException ex = new BusinessException(ErrorCode.ROBOT_NOT_FOUND);

        // When
        ResponseEntity<ApiResponse<Void>> response = exceptionHandler.handleBusinessException(ex, request);

        // Then
        assertEquals(HttpStatus.BAD_REQUEST, response.getStatusCode());
        assertEquals(ErrorCode.ROBOT_NOT_FOUND.getCode(), response.getBody().getCode());
        assertEquals(ErrorCode.ROBOT_NOT_FOUND.getMessage(), response.getBody().getMessage());
    }

    @Test
    @DisplayName("处理资源不存在异常")
    void handleResourceNotFound_ShouldReturnCorrectResponse() {
        // Given
        ResourceNotFoundException ex = new ResourceNotFoundException("故障规则", 999L);

        // When
        ResponseEntity<ApiResponse<Void>> response = exceptionHandler.handleBusinessException(ex, request);

        // Then
        assertEquals(HttpStatus.BAD_REQUEST, response.getStatusCode());
        assertEquals(ErrorCode.RESOURCE_NOT_FOUND.getCode(), response.getBody().getCode());
        assertTrue(response.getBody().getMessage().contains("故障规则不存在"));
    }

    @Test
    @DisplayName("处理通用异常")
    void handleException_ShouldReturnInternalServerError() {
        // Given
        Exception ex = new RuntimeException("未知错误");

        // When
        ResponseEntity<ApiResponse<Void>> response = exceptionHandler.handleException(ex, request);

        // Then
        assertEquals(HttpStatus.INTERNAL_SERVER_ERROR, response.getStatusCode());
        assertEquals(ErrorCode.SYSTEM_ERROR.getCode(), response.getBody().getCode());
    }

    @Test
    @DisplayName("处理非法参数异常")
    void handleIllegalArgument_ShouldReturnBadRequest() {
        // Given
        IllegalArgumentException ex = new IllegalArgumentException("参数错误");

        // When
        ResponseEntity<ApiResponse<Void>> response = exceptionHandler.handleIllegalArgument(ex, request);

        // Then
        assertEquals(HttpStatus.BAD_REQUEST, response.getStatusCode());
        assertEquals(ErrorCode.PARAM_ERROR.getCode(), response.getBody().getCode());
    }

    @Test
    @DisplayName("处理非法状态异常")
    void handleIllegalState_ShouldReturnConflict() {
        // Given
        IllegalStateException ex = new IllegalStateException("状态冲突");

        // When
        ResponseEntity<ApiResponse<Void>> response = exceptionHandler.handleIllegalState(ex, request);

        // Then
        assertEquals(HttpStatus.CONFLICT, response.getStatusCode());
        assertEquals(ErrorCode.RESOURCE_CONFLICT.getCode(), response.getBody().getCode());
    }
}
