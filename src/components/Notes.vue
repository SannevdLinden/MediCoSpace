<template>
  <div class="scroll height_95" id="notes_container">
    <div v-if="notes_id_display[0][1]">
      <!-- display the note titles, text and attached quant data button if there is data-->
      <div
        v-for="note in notes_id_display[0][1].slice().reverse()"
        v-bind:key="note.id"
        :id="note.id"
        style="padding-right:1rem; margin-top:1rem;"
      >
        <div class="display_flex" style="justify-content: space-between;">
          <div>
            <h3 style="font-weight:bold">
              NOTE {{ note.id + 1 }}: {{ note.title }}
              <span style="font-size:small"
                >{{ note.date_start.substring(0, 2) }}
                {{ months[parseInt(note.date_start.substring(3, 5)) - 1] }}
                {{ note.date_start.substring(6, 10) }}
              </span>
            </h3>
          </div>          
        </div>
        <br />
        <p :id="'note_text' + note.id" v-html="note.text"></p>       
      </div>
    </div>
  </div>
</template>

<script>
import sentences from '../assets/16961_sent_text.json'

export default {
  name: "NotesList",
  props: ["notes_id_display"], //notes to display
  data() {
    return {
      search_text: false, //if the yellow marking of matches to the search should be displayed
      search: "", //searched terms
      //search_result: "", //search synonyms 
      search_executed: false, //if search was done
      prev_highlight_word: "", //previous summary word the user clicked on to highlight 
      prev_highlight_word_fab: [], //previous concept space concept the user clicked on to highlight 
      months: [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
      ],
    };
  },
  methods: {
    //highlight words in text in color from the search actions or the action where the user clicked on a summary word
    //if highlighted word comes from a search action
    highlight_word(word, color, search) {
      //reset highlight
      if (word == "") {
        for (let i = 0; i < this.notes_id_display[0][1].length; i++) {
          let id = this.notes_id_display[0][1][i].id;
          let text = document.getElementById("note_text" + id).innerHTML;
          if (!search) {
            //clear the previous span
            text = text.replace(/style="color:red"/g, "");
          }
          document.getElementById("note_text" + id).innerHTML = text;
        }
      } else {        
        word = word.toLowerCase();        
        for (let i = 0; i < this.notes_id_display[0][1].length; i++) {
          let id = this.notes_id_display[0][1][i].id;
          let text = document.getElementById("note_text" + id).innerHTML;
          if (!search) {
            //clear the previous span
            text = text.replace(/style="color:red"/g, "");
            document.getElementById("note_text" + id).innerHTML = text;
          }          
            let final_text = "";
            let char_counter = 0;
            let text_array = text.toLowerCase();
            text_array = text_array.split(word);
            //mark all occurences of the to be highlighted word by injecting colors spans around the word(s)
            for (let j = 0; j < text_array.length; j++) {
              if (j == text_array.length - 1) {
                // last part of the text
                if (text_array.length > 1) {
                  //text need to go till the end of the string
                  if (search) {
                    final_text +=
                      "<span style='background-color:var(--" +
                      color +
                      ")'>" +
                      text.substring(char_counter, char_counter + word.length) +
                      "</span>";
                  } else if (this.prev_highlight_word != word) {
                    final_text +=
                      "<span style='color:" +
                      color +
                      "'>" +
                      text.substring(char_counter, char_counter + word.length) +
                      "</span>";
                  }
                  char_counter += word.length;
                  final_text += text.substring(char_counter, text.length);
                } else {
                  //if the word does not occur return original text
                  final_text = text;
                }
              } else {
                if (j != 0) {
                  if (search) {
                    final_text +=
                      "<span style='background-color:var(--" +
                      color +
                      ")'>" +
                      text.substring(char_counter, char_counter + word.length) +
                      "</span>";
                  } else if (this.prev_highlight_word != word) {
                    final_text +=
                      "<span style='color:" +
                      color +
                      "'>" +
                      text.substring(char_counter, char_counter + word.length) +
                      "</span>";
                  }
                  char_counter += word.length;
                }
                final_text += text.substring(
                  char_counter,
                  char_counter + text_array[j].length
                );
                char_counter += text_array[j].length;
              }
            }
            document.getElementById("note_text" + id).innerHTML = final_text; 
        }
      }
    },
    //reset all highlighting related to a search action
    reset() {
      for (let i = 0; i < this.notes_id_display[0][1].length; i++) {
        let id = this.notes_id_display[0][1][i].id;
        let text = document.getElementById("note_text" + id).innerHTML;
        document.getElementById("note_text" + id).innerHTML = text.replaceAll(
          'style="background-color:var(--green)"',
          ""
        );
      }
    },
    highlight_heatmap(word, id){ 
      console.log(word);   
      word = word.toLowerCase();              
      console.log(id);
      console.log(document.getElementById("note_text" + id));
      let text = document.getElementById("note_text" + id).innerHTML;  
                    
      let final_text = "";
      let char_counter = 0;
      let text_array = text.toLowerCase();
      text_array = text_array.split(word);
      //mark all occurences of the to be highlighted word by injecting colors spans around the word(s)
      for (let j = 0; j < text_array.length; j++) {
        if (j == text_array.length - 1) {
          // last part of the text
          if (text_array.length > 1) {
            //text need to go till the end of the string
            final_text +=
                "<span style='background-color:var(--green)'>" +
                text.substring(char_counter, char_counter + word.length) +
                "</span>";            
            char_counter += word.length;
            final_text += text.substring(char_counter, text.length);
          } else {
            //if the word does not occur return original text
            final_text = text;
          }
        } else {
          if (j != 0) {
            final_text +=
              "<span style='background-color:var(--green)'>" +
              text.substring(char_counter, char_counter + word.length) +
              "</span>";            
            char_counter += word.length;
          }
          final_text += text.substring(
            char_counter,
            char_counter + text_array[j].length
          );
          char_counter += text_array[j].length;
        }
      }
      document.getElementById("note_text" + id).innerHTML = final_text; 
    }

  },
  watch: {
    notes_id_display() {
      console.log('watch notes');
      //user clicked on other word/concept in word summary      
      if (this.notes_id_display[0][2] || this.notes_id_display[0][2] == "") {
        setTimeout(
          () => this.highlight_word(this.notes_id_display[0][2], "red", false),
          100
        );
      }

      //scroll to note corresponding to the button the user clicked
      const elmnt = document.getElementById(
        String(this.notes_id_display[0][0])
      );
      if (elmnt) {
        setTimeout(() => elmnt.scrollIntoView(), 100);
      }
      this.$emit("notes-loaded");

      //if search is executed
      if (
        this.notes_id_display[1] == true &&
        this.notes_id_display[0][1] 
      ) {
        
        this.search_text = this.notes_id_display[1];
        this.search = this.notes_id_display[2];
        for (let i = 0; i < this.notes_id_display[0][1].length; i++) {
          let note = this.notes_id_display[0][1][i].text;
          note = note.toLowerCase();
          if (note.includes(this.search.toLowerCase())) {
            setTimeout(
              () => this.highlight_word(this.search, "green", true),
              100
            );
          }
        }
        
      }
      //reset search
      if (
        (this.notes_id_display[2] == "") &&
        this.notes_id_display[0][1]
      ) {
        this.search = "";
        setTimeout(() => this.reset(), 100);
      }

      //highlight heatmap 
      if(this.notes_id_display[3] && this.notes_id_display[0][1]){
      let dict, concepta_text, conceptb_text;
      let current_open_notes = [];
      for (let i = 0; i < this.notes_id_display[0][1].length; i++) {
          current_open_notes.push(this.notes_id_display[0][1][i].id);
      }
      console.log(current_open_notes);
      for(let i = 0; i < this.notes_id_display[3][2].length; i++){
        if(current_open_notes.includes(this.notes_id_display[3][2][i])){        
          dict = sentences[this.notes_id_display[3][2][i]];
          concepta_text = dict[this.notes_id_display[3][0]];
          conceptb_text = dict[this.notes_id_display[3][1]];
          console.log(dict);
          if(concepta_text == conceptb_text){
            setTimeout(
              () => this.highlight_heatmap(concepta_text, this.notes_id_display[3][2][i]),
              200
            );          
          } else {
            setTimeout(
              () => this.highlight_heatmap(concepta_text, this.notes_id_display[3][2][i]),
              200
            );
            setTimeout(
              () => this.highlight_heatmap(conceptb_text, this.notes_id_display[3][2][i]),
              200
            );
          }          
        }
      }      
    }
    },
  },
  mounted() {
    console.log('mounted notes');
    
    
  },
};
</script>

<style scoped>
.height_95 {
  height: 64vh;
}
</style>
