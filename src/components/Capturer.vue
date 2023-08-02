<template>
  <div >
    <h2 class='header'>Current consult with patient</h2>
    <textarea
      id = 'cap'
      class="input"
      type="text"
      placeholder="Write your note here."
      v-on:keyup.enter="note_saved"
    /> <br>
    <input
      type="reset"
      value="Reset"
      v-on:click="remove_text"
      class="button button_style"
      style="padding-top:4px;"
    />
    <button
      v-on:click="note_saved"
      class="button button_style"
      style="margin-left:0.5rem"
    >
      Save
    </button>
    
  </div>
</template>

<script>
export default {
  name: 'Capturer',
  props: {
    
  }, 
  data (){
    return {
      text: {
            "id": 111,
            "date_start": "16-07-1988",
            "cluster": "check_up_6",
            "title": "ECG",
            "department": [
                "ECG"
            ],
            "text": "Check up on patient with \"arrhythmia\" <disease>. "
        }
    }
  }, 
  methods: {
    note_saved(){
      this.$emit("note-saved", this.text);
    }, 
    remove_text(){
      document.getElementById("cap").value = "";
    }

  }, 
  mounted() {
    document.getElementById("cap").value = this.text.text;
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
.input{
  width: 95%;
  height: 16vh;
}
</style>
