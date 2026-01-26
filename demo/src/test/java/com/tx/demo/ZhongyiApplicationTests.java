package com.tx.demo;

import com.tx.demo.entity.Question;
import com.tx.demo.mapper.QuestionMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.List;

@SpringBootTest
class ZhongyiApplicationTests {


	@Autowired
	private QuestionMapper questionMapper;
	@Test
	public void findAll(){
		List<Question> questions=questionMapper.selectAllQuestions();
		questions.forEach(question -> System.out.println(question));
	}

}
