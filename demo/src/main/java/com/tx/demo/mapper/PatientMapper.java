package com.tx.demo.mapper;

import com.tx.demo.entity.Patient;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

@Mapper
public interface PatientMapper {
    Patient findByIdCard(@Param("idCard")String idCard);

    int update(Patient patient);

    int insert(Patient patient);
    // 增加：查询最近一次登记的病人ID
    @Select("SELECT id FROM patients ORDER BY id DESC LIMIT 1")
    Long findLastId();

}
