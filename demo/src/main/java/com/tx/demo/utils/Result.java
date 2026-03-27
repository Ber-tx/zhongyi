package com.tx.demo.utils;

import lombok.Data;

@Data
public class Result {
    private Integer code; // 200表示成功，500表示失败
    private String msg;   // "操作成功"
    private Object data;       // 真正的数据（比如题目列表）

    //请求成功,前端需要返回数据库数据,传入的object就是要返回的数据库数据
    public static Result success(Object object){
        Result result=new Result();
        result.code=200;
        result.msg="success";
        result.data=object;
        return result;
    }
    //请求成功，前端不需要数据库数据的
    public static Result success(){
        Result result=new Result();
        result.code=200;
        result.msg="success";
        return result;
    }
    
    //请求成功，带自定义消息和数据
    public static Result success(Object object, String msg){
        Result result=new Result();
        result.code=200;
        result.msg=msg;
        result.data=object;
        return result;
    }
    
    //请求失败，返回失败内容

    public static Result error(String msg){
        Result result=new Result();
        result.code=500;
        result.msg=msg;
        return result;
    }


}
