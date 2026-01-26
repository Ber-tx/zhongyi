package com.tx.demo.mapper;

import com.tx.demo.entity.Question;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import java.util.List;

@Mapper
public interface QuestionMapper {

    // 使用 as 别名手动对应实体类的属性名
    @Select("SELECT id, content, " +
            "is_reverse as isReverse, " +
            "sort, " +
            "constitution_codes as constitutionCodes " + // 关键点：对应你的 String constitutionCodes
            "FROM question " +
            "ORDER BY sort ASC")
    List<Question> selectAllQuestions();

}