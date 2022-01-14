<template>
  <div class="display_flex">
    <!-- horizontal bar connecting cluster to timeline-->
    <div
      class="bar_to_cluster_stripe"
      :style="stripe_background"
      style="width:5%; margin-top:25px;"
      :id="'cluster_stripe' + cluster[0].id"
      v-if="!cluster[5]"
    ></div>
    <!-- cluster summary box -->
    <div
      class="cluster_box"
      :style="cluster_background"
      :id="'cluster_' + cluster[0].id"
      v-if="cluster[0].date_stop"
      style="width:100%;"
    >
      <div style="padding:1rem;">
        <div class="display_flex" style="justify-content: space-between;">
          <div>
            <span style="font-weight: bold;"
              >CLUSTER: {{ cluster[0].title }}:
            </span>
            <span
              v-for="(dep, ind) in cluster[0].department"
              v-bind:key="ind"
              style="font-weight: bold;"
              >{{ dep }},
            </span>
            <span
              style="font-weight: bold; font-size:small"
              v-if="cluster[0].date_stop != cluster[0].date_start"
            >
              {{ cluster[0].date_start.substring(0, 2) }}
              {{ months[parseInt(cluster[0].date_start.substring(3, 5)) - 1] }}
              {{ cluster[0].date_start.substring(6, 10) }} till
              {{ cluster[0].date_stop.substring(0, 2) }}
              {{ months[parseInt(cluster[0].date_stop.substring(3, 5)) - 1] }}
              {{ cluster[0].date_stop.substring(6, 10) }}</span
            >
            <span
              style="font-weight: bold; font-size:small"
              v-if="cluster[0].date_stop == cluster[0].date_start"
            >
              {{ cluster[0].date_start.substring(0, 2) }}
              {{ months[parseInt(cluster[0].date_start.substring(3, 5)) - 1] }}
              {{ cluster[0].date_start.substring(6, 10) }}
            </span>
          </div>          
        </div>
        <!-- summary words-->
        <div style="margin-top: 0.5rem">           
          <!-- summary disease words -->          
          <div v-if="cluster[0].disease_words.length > 0">
            <span style="font-weight: bold;">Diseases:</span>
            <span
              v-for="(word, index) in cluster[0].disease_words"
              v-bind:key="index"
            >
              <span
                v-if="index != cluster[0].disease_words.length - 1"
                :id="'word_' + word.toLowerCase()"
                v-on:click="highlight_word(word)"
              >
                {{ word }}</span
              >
              <span v-if="index != cluster[0].disease_words.length - 1"
                >,</span
              >
              <span
                v-if="index == cluster[0].disease_words.length - 1"
                :id="'word_' + word.toLowerCase()"
                v-on:click="highlight_word(word)"
              >
                {{ word }}</span
              >
            </span>
          </div>
      
          <!-- drugs summary words-->          
          <div v-if="cluster[0].drugs_words.length > 0">
            <span style="font-weight: bold;">Drugs:</span>
            <span
              v-for="(word, index) in cluster[0].drugs_words"
              v-bind:key="index"
            >
              <span
                v-if="index != cluster[0].drugs_words.length - 1"
                :id="'word_' + word.toLowerCase()"
                v-on:click="highlight_word(word)"
              >
                {{ word }}</span
              >
              <span v-if="index != cluster[0].drugs_words.length - 1">,</span>
              <span
                v-if="index == cluster[0].drugs_words.length - 1"
                :id="'word_' + word.toLowerCase()"
                v-on:click="highlight_word(word)"
              >
                {{ word }}</span
              >
            </span>
          </div>
         
          <!-- summary procedure words-->          
          <div v-if="cluster[0].procedure_words.length > 0">
            <span style="font-weight: bold;">Procedures:</span>
            <span
              v-for="(word, index) in cluster[0].procedure_words"
              v-bind:key="index"
            >
              <span
                v-if="index != cluster[0].procedure_words.length - 1"
                :id="'word_' + word.toLowerCase()"
                v-on:click="highlight_word(word)"
              >
                {{ word }}</span
              >
              <span v-if="index != cluster[0].procedure_words.length - 1"
                >,</span
              >
              <span
                v-if="index == cluster[0].procedure_words.length - 1"
                :id="'word_' + word.toLowerCase()"
                v-on:click="highlight_word(word)"
              >
                {{ word }}</span
              >
            </span>
          </div>
          
          <!-- note buttons-->
          <div>
            <h4 style="font-weight: bold;">Notes:</h4>
            <div class="buttons">
              <div
                v-for="(note, ind) in cluster[1].slice().reverse()"
                v-bind:key="ind"
              >
                <div
                  v-if="search_previews[cluster[1].length - 1 - ind]"
                  class="tooltip"
                  :id="'button_' + note[0]"
                >
                  <button
                  :id="'button_detail_' + note[0]"
                    v-if="
                      search_previews[cluster[1].length - 1 - ind].length > 0
                    "
                    v-on:click="open_note(note[0])"
                    class="button button_style button_note"
                    style="margin-right: 0.5rem; background-color: #F6BE00 !important; color:var(--darkest-grey) !important; 
                                        border: 2px solid !important;"
                  >
                    {{ note[0] + 1 }}. {{ note[3].substring(0, 3) }}
                  </button>

                  <div
                    v-if="
                      search_previews[cluster[1].length - 1 - ind].length > 0
                    "
                    class="tooltiptext"
                    :id="'snippet_' + note[0]"
                  >
                    <p
                      v-for="(snippet, i) in search_previews[
                        cluster[1].length - 1 - ind
                      ]"
                      v-bind:key="i"
                    >
                      ... {{ snippet }} ...
                    </p>
                    <span
                      class="tooltip_arrow"
                      :id="'snippet_arrow_' + note[0]"
                    ></span>
                  </div>

                  <button
                    v-if="
                      !search_previews[cluster[1].length - 1 - ind].length > 0
                    "
                    v-on:click="open_note(note[0])"
                    :id="'button_detail_' + note[0]"
                    class="button button_style button_note"
                    style="margin-right: 0.5rem;"
                  >
                    {{ note[0] + 1 }}. {{ note[3].substring(0, 3) }}
                  </button>
                </div>


                <div
                  v-if="!search_previews[cluster[1].length - 1 - ind] && !heat_high"
                  :id="'button_' + note[0]"
                >
                  <button
                    :id="'button_detail_' + note[0]"
                    v-if="!search_previews[cluster[1].length - 1 - ind]"
                    v-on:click="open_note(note[0])"
                    class="button button_style button_note"
                    style="margin-right: 0.5rem;"
                  >
                    {{ note[0] + 1 }}. {{ note[3].substring(0, 3) }}
                  </button>
                </div>


                <div
                  v-if="!search_previews[cluster[1].length - 1 - ind] && heat_high"
                  :id="'button_' + note[0]"
                >
                  <button
                    :id="'button_detail_' + note[0]"
                    v-if="cluster[4][2].includes(note[0])"
                    v-on:click="open_note(note[0])"
                    class="button button_style button_note"
                    style="margin-right: 0.5rem; background-color: #F6BE00 !important; color:var(--darkest-grey) !important; 
                                        border: 2px solid !important;"
                  >
                    {{ note[0] + 1 }}. {{ note[3].substring(0, 3) }}
                  </button>

                   <button
                    :id="'button_detail_' + note[0]"
                    v-if="!cluster[4][2].includes(note[0])"
                    v-on:click="open_note(note[0])"
                    class="button button_style button_note super"
                    style="margin-right: 0.5rem;"
                  >
                    {{ note[0] + 1 }}. {{ note[3].substring(0, 3) }}
                  </button>
                </div>


              </div>
            </div>
          </div>
        </div>
      </div>
    </div>   
  </div>
</template>

<script>
export default {
  name: "Cluster",
  props: ["cluster"], //[cluster, [[id note, date note, text, title], [id note, date note, text, title],...], search_text, search, search_result]
  data() {
    return {
      prev_word: "", //previously clicked summary word
      same_word_count: 0, //checks if previous words is the same word as the word the user currently clicked on
      search_text: false, //display yellow marking search results
      search: "", //searched term
      search_previews: [], //previews of search hits, per note in cluster > ['text text text', 'text text text']
      notes: [], // all notes belonging to this cluster [[id, date, text, snippets], ]
      search_hits: [], //summary words that match need yellow marking
      cluster_color: { //color background cluster box
        color: "var(--grey)",
      },
      cluster_background: {
        backgroundColor: "var(--grey)",
      },
      stripe_background: {
        backgroundColor: "var(--grey)",
      },
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
      heat_high: false
    };
  },
  methods: {
    //highlight word in word summary if user clicks on it
    //word is the word(s) to be highlighted
    highlight_word(word) {
      word = word.toLowerCase();
      if (this.prev_word != "") {
        let prev_pNode = document.getElementById("word_" + this.prev_word);
        prev_pNode.innerHTML = "<span> " + this.prev_word + "</span>";
      }
      let pNode = document.getElementById("word_" + word);
      if (word == this.prev_word) {
        if (this.same_word_count % 2 != 0) {
          pNode.innerHTML =
            "<span style='color:var(--red);'> " + word + "</span>";
        } else {
          pNode.innerHTML = "<span> " + word + "</span>";
        }
        this.same_word_count++;
      } else {
        pNode.innerHTML =
          "<span style='color:var(--red);'> " + word + "</span>";
        this.same_word_count = 0;
      }
      this.prev_word = word;      
      this.$emit("highlight-word", [
        word,
        this.cluster[1][0][0],
        this.same_word_count,
      ]); //id of the first note
      
    },
    //check is search term or a synonym is a summary word in cluster, if yes > mark it yellow
    search_words(word) {
      word = word.toLowerCase();
      let pNode = document.getElementById("word_" + word);
      pNode.innerHTML =
        "<span style='background-color:var(--green);'>" + word + "</span>";
      this.search_hits.push(word);
     },
    //display search previews, word = word contained in search that is present in a note, id = id of that note
    previews(word, id) {
      word = word.toLowerCase();
      let note_text_org = this.notes[id][2];
      let note_text = note_text_org;
      note_text = note_text.replace(/(\r\n|\n|\r)/gm, "");
      //searched terms contains spaces
      if (word.split(" ").length > 1) {
        let word_split = word.split(" ");
        let new_word = "";
        for (let j = 0; j < word_split.length; j++) {
          if (j == 0) {
            new_word += word_split[j];
          } else {
            new_word += "A" + word_split[j];
          }
        }
        note_text = note_text.toLowerCase();
        note_text = note_text.replace(word, new_word);
        note_text = note_text
          .replace(/[^\w\s]|_/g, function($1) {
            return " " + $1 + " ";
          })
          .replace(/[ ]+/g, " ")
          .split(" ");
        word = new_word;
      } else {
        note_text = note_text.toLowerCase();
        //split on punctuation and whitespaces
        note_text = note_text
          .replace(/[^\w\s]|_/g, function($1) {
            return " " + $1 + " ";
          })
          .replace(/[ ]+/g, " ")
          .split(" ");
      }
      //if searched term does not contain spaces
      if (note_text.includes(word)) {
        let ind_word = this.getAllIndexes(word, note_text);
        for (let j = 0; j < ind_word.length; j++) {
          let string_snippet = "";
          let start = ind_word[j] - 5;
          let stop = ind_word[j] + 7;
          if (start < 0) {
            start = 0;
          }
          if (stop > note_text.length - 1) {
            stop = note_text.length - 1;
          }
          let tmp = note_text.slice(start, stop);
          for (let k = 0; k < tmp.length; k++) {
            string_snippet += tmp[k] + " ";
          }
          if (string_snippet.includes("A")) {
            string_snippet = string_snippet.replace("A", " ");
          }
          this.search_previews[id].push(string_snippet);
        }
        setTimeout(() => this.snippet_display(this.cluster[1][id][0]), 100);
      }
    },
    //get all indexes of notes that contain a certain string
    //searchStr = string to search for, str= note text
    getAllIndexes(searchStr, str) {
      var searchStrLen = searchStr.length;
      if (searchStrLen == 0) {
        return [];
      }
      var startIndex = 0,
        index,
        indices = [];
      while ((index = str.indexOf(searchStr, startIndex)) > -1) {
        indices.push(index);
        startIndex = index + searchStrLen;
      }
      return indices;
    },
    //open notes from this cluster on the side, and scroll automatically to 'note' 
    open_note(note) {
      this.$emit("open-note", note);
    },
    //display snippets of note where id is 'id'
    snippet_display(id) {
      if (document.getElementById("cluster_" + this.cluster[0].id)) {
        let element = document.getElementById("button_" + id);
        let element_offset = element.offsetLeft;
        let cluster_offset = document.getElementById(
          "cluster_" + this.cluster[0].id
        ).offsetLeft;
        let width =
          "calc(" +
          String(
            document.getElementById("cluster_" + this.cluster[0].id).clientWidth
          ) +
          "px - 2rem )";
        if (document.getElementById("snippet_" + id)) {
          let margin_left =
            "calc(" +
            String(-1 * (element_offset - cluster_offset)) +
            "px + 1rem )";
          document.getElementById(
            "snippet_" + id
          ).style.marginLeft = margin_left;
          document.getElementById("snippet_" + id).style.width = width;
          document.getElementById("snippet_arrow_" + id).style.marginLeft =
            String(element_offset - cluster_offset + 20) + "px";
        }
      }
    }
  },
  watch: {
    cluster() {
      console.log('cluster');
      // color button yellow selection heatmap
      console.log(this.cluster[4]);
      if(this.cluster[4]){
        console.log('in loop');
        this.heat_high = true;
      } else {
        this.heat_high = false;
      }

      this.notes = this.cluster[1];
      
      //if a search is executed 
      if (this.cluster[2] == true && this.cluster[4] != "no results") {
        //make preview snippets empty array length of amount of notes
        this.search_previews = [];
        for (let i = 0; i < this.notes.length; i++) {
          this.search_previews.push([]);
        }
        this.search_text = this.cluster[2];
        this.search = this.cluster[3];
        if (this.search_text == true && !this.cluster[0].text) {
          //check if it is not a note cluster
          for (let i = 0; i < this.cluster[0].procedure_words.length; i++) {
            if (
              this.cluster[0].procedure_words[i].toLowerCase() ==
              this.search.toLowerCase()
            ) {
              this.search_words(this.cluster[0].procedure_words[i]);
            }
          }
          for (let i = 0; i < this.cluster[0].disease_words.length; i++) {
            if (
              this.cluster[0].disease_words[i].toLowerCase() ==
              this.search.toLowerCase()
            ) {
              this.search_words(this.cluster[0].disease_words[i]);
            }
          }
          for (let i = 0; i < this.cluster[0].drugs_words.length; i++) {
            if (
              this.cluster[0].drugs_words[i].toLowerCase() ==
              this.search.toLowerCase()
            ) {
              this.search_words(this.cluster[0].drugs_words[i]);
            }            
          }
        }
        //preview snippets
        if (this.cluster[0].text) {
          let note = this.cluster[0].text; //get the text of the note
          note = note.toLowerCase();
          if (note.includes(this.search.toLowerCase())) {
            setTimeout(() => this.previews(this.search, 0), 100);
          }
          
        } else {
          for (let i = 0; i < this.cluster[1].length; i++) {
            let note = this.cluster[1][i][2]; //get the text of the note
            note = note.toLowerCase();
            if (note.includes(this.search.toLowerCase())) {
              setTimeout(() => this.previews(this.search, i), 100);
            }
            
          }
        }

      } else if (this.cluster[2] == false || this.cluster[4] == "no results") { //no search executed
        this.search_text = false;
        if (this.search != "" && this.search_hits) { //reset yellow markings
          for (let i = 0; i < this.search_hits.length; i++) {
            document.getElementById(
              "word_" + this.search_hits[i]
            ).innerHTML = this.search_hits[i];
          }
          this.search_hits = [];
        }
      }
    },
  },
  created() {
    console.log('cluster crea');
    if (this.cluster[0].name) {
      //then this is a cluster summary box
      if (this.cluster[0].name.includes("check_up")) {
        this.cluster_color.color = "var(--blue)";
        this.cluster_background.backgroundColor = "var(--blue-opac)";
        this.stripe_background.backgroundColor = "var(--blue)";
      } else if (this.cluster[0].name.includes("admis")) {
        this.cluster_color.color = "var(--orange)";
        this.cluster_background.backgroundColor = "var(--orange-opac)";
        this.stripe_background.backgroundColor = "var(--orange)";
      }
    }
    // color button yellow selection heatmap
    console.log(this.cluster[4]);
    if(this.cluster[4]){
      this.heat_high = true;
    } 
    
  },
};
</script>

<style scoped>
.super{}

.cluster_box {
  margin: 0.5rem 0;
}

.inline {
  display: inline-block;
  vertical-align: top;
}

.link {
  color: var(--lightest-grey);
  text-decoration: none;
}

.link:hover {
  color: var(--lightest-grey);
  text-decoration: none;
  cursor: pointer;
}

.tooltip {
  position: relative;
}

.tooltiptext {
  visibility: hidden;
  width: 300%;
  background-color: var(--darkest-grey);
  color: var(--lightest-grey);
  border-radius: 6px;
  padding: 0.5rem;
  position: absolute;
  z-index: 2;
}

.tooltip_arrow {
  content: "";
  position: absolute;
  margin-left: -5px;
  border-width: 5px;
  bottom: 100%;
  border-style: solid;
  border-color: transparent transparent var(--darkest-grey) transparent;
}

.tooltip:hover .tooltiptext {
  visibility: visible;
}
</style>
