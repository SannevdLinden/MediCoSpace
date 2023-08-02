<template>
  <div class="font_size_small">
    <div class="font_size_small">
    <!-- display all general patient information-->
      <table style="table-layout: auto; width: 100%;">
        <tr>
          <th style="vertical-align: middle !important; ">
            <span class="bold">Name:</span>
          </th>
          <th class="table_padding_left">
            <span style="font-size:large;">{{
              data.generalPatientInfo.name
            }}</span>
          </th>
        </tr>
        <tr>
          <th class="bold">Gender:</th>
          <th class="table_padding_left">{{ data.generalPatientInfo.gender }}</th>
        </tr>
        <tr>
          <th class="bold">Age:</th>
          <th class="table_padding_left">{{ data.generalPatientInfo.age }}</th>
        </tr>
        <tr>
          <th class="bold">Height:</th>
          <th class="table_padding_left">
            {{ data.generalPatientInfo.height }} m
          </th>
        </tr>
        <tr>
          <th class="bold">Weight:</th>
          <th class="table_padding_left">
            {{ data.generalPatientInfo.weight }} kg
          </th>
        </tr>

        <tr>
          <th class="bold">Allergies:</th>
          <th class="table_padding_left">
            {{ data.generalPatientInfo.allergies }}
          </th>
        </tr>
        <tr>
          <th class="bold">Medical Staff:</th>
          <th class="table_padding_left">
            {{ data.generalPatientInfo.medical_staff }}
          </th>
        </tr>
        <tr>
          <th class="bold">Medical History:</th>
          <th class="table_padding_left">
            {{ data.generalPatientInfo.history_illness }}
          </th>
        </tr>
        <tr>
          <th class="bold">Social History:</th>
          <th class="table_padding_left">
            {{ data.generalPatientInfo.social_history }}
          </th>
        </tr>
        <tr>
          <th class="bold">Family History:</th>
          <th class="table_padding_left">
            {{ data.generalPatientInfo.family_history }}
          </th>
        </tr>
      </table>
    </div>    
  </div>
</template>

<script>
import generalPatientInfo from "../assets/generalPatientInfo.json";

export default {
  name: 'PatientInfo',
  data() {
    return {
      data: [],
    };
  },
  created() {
    this.data = generalPatientInfo;
    console.log(this.data.generalPatientInfo.name);
  },
}
</script>


<style scoped>
.font_size_small {
  font-size: 14px;
}
</style>
