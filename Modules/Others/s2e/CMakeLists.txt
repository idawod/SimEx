INCLUDE(ExternalProject)

ExternalProject_Add(
s2e
URL  https://github.com/chuckie82/simS2E/archive/master.zip
CONFIGURE_COMMAND ""
CMAKE_COMMAND ""
PATCH_COMMAND cp ${CMAKE_CURRENT_SOURCE_DIR}/pmi_demo.py.patch packages/pmi_demo/pmi_demo.py
BUILD_COMMAND ""
INSTALL_COMMAND ""
)

ExternalProject_Get_Property(s2e SOURCE_DIR)

install(FILES ${SOURCE_DIR}/modules/diffr/prepHDF5.py
        DESTINATION  ${PYPATH})

install(FILES ${SOURCE_DIR}/packages/pmi_demo/pmi_demo.py
        DESTINATION  ${PYPATH})

install(FILES ${SOURCE_DIR}/modules/pmi/script.py
        DESTINATION  ${PYPATH}
        RENAME pmi_script.py)

