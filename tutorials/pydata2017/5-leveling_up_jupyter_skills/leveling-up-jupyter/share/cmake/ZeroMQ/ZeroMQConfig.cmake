# ZeroMQ cmake module
# This module sets the following variables in your project::
#
#   ZeroMQ_FOUND - true if ZeroMQ found on the system
#   ZeroMQ_INCLUDE_DIR - the directory containing ZeroMQ headers
#   ZeroMQ_LIBRARY - 
#   ZeroMQ_STATIC_LIBRARY


####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was ZeroMQConfig.cmake.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

macro(check_required_components _NAME)
  foreach(comp ${${_NAME}_FIND_COMPONENTS})
    if(NOT ${_NAME}_${comp}_FOUND)
      if(${_NAME}_FIND_REQUIRED_${comp})
        set(${_NAME}_FOUND FALSE)
      endif()
    endif()
  endforeach()
endmacro()

####################################################################################

set(PN ZeroMQ)
set_and_check(${PN}_INCLUDE_DIR "${PACKAGE_PREFIX_DIR}/include")
set_and_check(${PN}_LIBRARY "${PACKAGE_PREFIX_DIR}/lib/libzmq.so")
set_and_check(${PN}_STATIC_LIBRARY "${PACKAGE_PREFIX_DIR}/lib/libzmq.a")
check_required_components(${PN})
