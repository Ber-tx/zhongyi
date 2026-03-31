package com.tx.demo.vo;

/**
 * 身份证信息视图对象
 */
public class IdCardInfoVO {
    
    private String idNumber;           // 身份证号码
    private String name;               // 姓名
    private String gender;             // 性别 (M/F)
    private String nationality;        // 民族
    private String dateOfBirth;        // 出生日期 (YYYY-MM-DD)
    private String address;            // 地址
    private String issuingAuthority;   // 签发机构
    private String validFrom;          // 有效期起始 (YYYY-MM-DD)
    private String validTo;            // 有效期终止 (YYYY-MM-DD)
    private String photoBase64;        // 照片数据 (Base64)
    private String idCardImageBase64;  // 身份证整卡预览图 (Base64 或 data URL)

    // Getters and Setters
    public String getIdNumber() {
        return idNumber;
    }

    public void setIdNumber(String idNumber) {
        this.idNumber = idNumber;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getGender() {
        return gender;
    }

    public void setGender(String gender) {
        this.gender = gender;
    }

    public String getNationality() {
        return nationality;
    }

    public void setNationality(String nationality) {
        this.nationality = nationality;
    }

    public String getDateOfBirth() {
        return dateOfBirth;
    }

    public void setDateOfBirth(String dateOfBirth) {
        this.dateOfBirth = dateOfBirth;
    }

    public String getAddress() {
        return address;
    }

    public void setAddress(String address) {
        this.address = address;
    }

    public String getIssuingAuthority() {
        return issuingAuthority;
    }

    public void setIssuingAuthority(String issuingAuthority) {
        this.issuingAuthority = issuingAuthority;
    }

    public String getValidFrom() {
        return validFrom;
    }

    public void setValidFrom(String validFrom) {
        this.validFrom = validFrom;
    }

    public String getValidTo() {
        return validTo;
    }

    public void setValidTo(String validTo) {
        this.validTo = validTo;
    }

    public String getPhotoBase64() {
        return photoBase64;
    }

    public void setPhotoBase64(String photoBase64) {
        this.photoBase64 = photoBase64;
    }

    public String getIdCardImageBase64() {
        return idCardImageBase64;
    }

    public void setIdCardImageBase64(String idCardImageBase64) {
        this.idCardImageBase64 = idCardImageBase64;
    }

    @Override
    public String toString() {
        return "IdCardInfoVO{" +
                "idNumber='" + idNumber + '\'' +
                ", name='" + name + '\'' +
                ", gender='" + gender + '\'' +
                ", nationality='" + nationality + '\'' +
                ", dateOfBirth='" + dateOfBirth + '\'' +
                ", address='" + address + '\'' +
                ", issuingAuthority='" + issuingAuthority + '\'' +
                ", validFrom='" + validFrom + '\'' +
                ", validTo='" + validTo + '\'' +
                ", hasPhoto=" + (photoBase64 != null && !photoBase64.isEmpty()) +
                ", hasCardImage=" + (idCardImageBase64 != null && !idCardImageBase64.isEmpty()) +
                '}';
    }
}
