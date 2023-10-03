cmake_minimum_required(VERSION 3.1)
project(paulplugin)


set(CMAKE_CXX_FLAGS -Wl,--no-as-needed)
add_compile_options(-Wno-error=deprecated-declarations)
set(CMAKE_BUILD_TYPE RelWithDebInfo CACHE STRING "FORCE VALUE" FORCE)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS OFF)
set(CMAKE_CUDA_COMPILER /usr/local/cuda/bin/nvcc CACHE STRING "FORCE VALUE" FORCE)
set(CMAKE_CUDA_COMPILER /usr/local/cuda/bin/nvcc CACHE STRING "FORCE VALUE" FORCE)


#SOFA settings
set(SOFA_BUILD_TESTS ON CACHE BOOL "FORCE VALUE" FORCE)
set(SOFA_BUILD_METIS ON CACHE BOOL "FORCE VALUE" FORCE)
set(SOFA_USE_MASK OFF CACHE BOOL "FORCE VALUE" FORCE)
set(APPLICATION_MODELER OFF CACHE BOOL "FORCE VALUE" FORCE)
set(SOFA_BUILD_SCENECREATOR OFF CACHE BOOL "FORCE VALUE" FORCE)
set(SOFAGUI_ENABLE_QWT OFF CACHE BOOL "FORCE VALUE" FORCE)
set(PLUGIN_SOFAPYTHON OFF CACHE BOOL "FORCE VALUE" FORCE)
set(PLUGIN_SOFAPYTHON3 ON CACHE BOOL "FORCE VALUE" FORCE)
set(PLUGIN_IMAGE OFF CACHE BOOL "FORCE VALUE" FORCE)
set(PLUGIN_DIFFUSIONSOLVER OFF CACHE BOOL "FORCE VALUE" FORCE)

set(SOFA_FETCH_CGALPLUGIN ON CACHE BOOL "FORCE VALUE" FORCE)
set(PLUGIN_CGALPLUGIN ON CACHE BOOL "FORCE VALUE" FORCE)
set(SOFATERMINAL_BUILD_BINDINGS OFF CACHE BOOL "FORCE VALUE" FORCE)
set(SOFA_FETCH_REGRESSION ON CACHE BOOL "FORCE VALUE" FORCE)
set(APPLICATION_REGRESSION_TEST ON CACHE BOOL "FORCE VALUE" FORCE)



#Personal plugins
##### CUDA #####
#set(SOFACUDA_CUBLAS ON  CACHE BOOL "FORCE VALUE" FORCE)
#set(SOFACUDA_DOUBLE ON  CACHE BOOL "FORCE VALUE" FORCE)
#set(PLUGIN_SOFACUDA ON  CACHE BOOL "FORCE VALUE" FORCE)


#set_target_properties(SofaCUDA PROPERTIES CUDA_ARCHITECTURES "sm_8.6")

add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../../consortium/SofaPython3 "Plugin/SofaPython3")


add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../../hadrien/CollisionAlgorithm "Plugin/CollisionAlgorithm")
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../../hadrien/ConstraintGeometry "Plugin/ConstraintGeometry")
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../../hadrien/NeedleConstraintPlugin "Plugin/NeedleConstraintPlugin")


#[[
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../../sofa-framework/SofaCUDAUtils "Plugin/SofaCUDAUtils")
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../../sofa-framework/SofaAsyncSolvers "Plugin/SofaAsyncSolvers")
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../../sofa-framework/SofaCUDASolvers "Plugin/SofaCUDASolvers")
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../../sofa-framework/SofaCUDADev "Plugin/SofaCUDADev")


set_target_properties(SofaCUDAUtils PROPERTIES CUDA_ARCHITECTURES "sm_8.6")
set_target_properties(SofaAsyncSolvers PROPERTIES CUDA_ARCHITECTURES "sm_8.6")
set_target_properties(SofaCUDASolvers PROPERTIES CUDA_ARCHITECTURES "sm_8.6")
set_target_properties(SofaCUDADev PROPERTIES CUDA_ARCHITECTURES "sm_8.6")]]


