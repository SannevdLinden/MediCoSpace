<template>
  <div id="app">
    <div class='columns fourth-height' >
      <div class='column is-3 border_side_bottom padding_normal'>
         <h2 class="header">General Patient Information</h2>
          <div class="scroll max_height_width">
            <PatientInfo/>
          </div>
      </div>
      <div class='column border_side_bottom padding_normal'>
        <Capturer 
          v-on:note-saved="add_note"
        />
      </div>
      <div class='column is-3 border_bottom'>       
        <div class='columns' style='height:100%'>
          <div class="column is-7" style="margin-top: 0.3rem;">
             <!-- search bar, reset and submit button -->        
            <input
              id = 'search'
              class="input"
              type="text"
              placeholder="Search"
              v-model="search_tmp"
              v-on:keyup.enter="search_term"
            /> <br>
            <input
              type="reset"
              value="Reset"
              v-on:click="remove_search"
              class="button button_style"
              style="padding-top:4px;"
            />
            <button
              v-on:click="search_term"
              class="button button_style"
              style="margin-left:0.5rem"
            >
              Submit
            </button>

            <!-- cluster type filters -->
            <h3 class="sub_header">Cluster type:</h3>
            <div class='scroll' style='height:50%'>
            <div style="width:100%; opacity: 0.4;">
              <label class="is-checkbox">
                <input id="mycheckbox" type="checkbox" disabled />
                <span class="icon checkmark is-red" >
                  <font-awesome-icon
                    class="red-background"
                    :icon="['fas', 'check']"
                  />
                </span>
                <span
                  >ER without 
                  hospitalization</span
                >
              </label>
            </div>

            <label class="is-checkbox">
              <input
                id="mycheckbox"
                checked="checked"
                type="checkbox"
                v-bind:value="'Check-ups'"
                v-model="checkedBoxesType"
                v-on:change="filterNotes('Type', 'Check-ups')"
              />
              <span class="icon checkmark is-blue">
                <font-awesome-icon
                  class="blue-background"
                  :icon="['fas', 'check']"
                />
              </span>
              <span>Check-ups</span>
            </label>

            <div style="width:100%; opacity: 0.4;">
              <label class="is-checkbox">
                <input id="mycheckbox" type="checkbox" disabled />
                <span class="icon checkmark is-green">
                  <font-awesome-icon
                    class="green-background"
                    :icon="['fas', 'check']"
                  />
                </span>
                <span
                  >Small 
                  interventions</span
                >
              </label>
            </div>

            <label class="is-checkbox">
              <input
                id="mycheckbox"
                checked="checked"
                type="checkbox"
                v-bind:value="'Admission'"
                v-model="checkedBoxesType"
                v-on:change="filterNotes('Type', 'Admission')"
              />
              <span class="icon checkmark is-orange">
                <font-awesome-icon
                  class="orange-background"
                  :icon="['fas', 'check']"
                />
              </span>
              <span
                >Hospital
                admissions</span
              >
            </label> 
            </div> 
          </div> 
          <div class="column" style='margin-top: -0.5rem'>
            <!-- specialism filters -->            
            <h3 class="sub_header">Specialism:</h3>
            <div class='scroll' style='height:90%'>
            <div v-for="depart in departments" v-bind:key="depart">
              <label class="is-checkbox">
                <input
                  id="mycheckbox"
                  checked="checked"
                  type="checkbox"
                  v-bind:value="depart"
                  v-model="checkedBoxesSpecialism"
                  v-on:change="filterNotes('Specialism', depart)"
                />
                <span class="icon checkmark">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </span>
                <span>{{ depart }}</span>
              </label>
              <br />
            </div>
          </div> 
        </div> 
        </div>           
      </div>
    </div>


    <div class='columns threefourth-height'>
      <div class='column is-3 padding_normal' id='scatterplots'>
        <Scatter ref='scatter' v-bind:selection="scatter_filter"
          v-on:scatter_brush_concepts="scatter_select"/>
      </div>
      <div class='column is-5 padding_normal' id='heatmaps'>
        <Heatmap ref='heatmap' v-bind:time_filter="timeline_time_filter"
          v-on:concepts_scatter="scatter_filter_time"
          v-on:highlight_scatter='scatter_highlight'
          v-on:aggregated_heatmap='heatmap_aggr'
          v-on:notes-highlight='highlight_notes'
          v-on:axis_labels='save_axis_labels'/>
      </div>
      <div class='column'>
        <h2 class="header">Patient's notes on a timeline</h2>
        <Timeline v-bind:data_to_child="[
            notes_to_child,
            clustersNotes_to_child,
            search_text,
            search,
            display_notes,
            note_id_to_display,
            highlight
          ]"
          :key="data_changed"
          v-on:time_filtered='filter_time'
          v-on:time_filter_remove ='filter_time_remove'/>
      </div>
        
      
    </div>      
  </div>
</template>

<script>
import PatientInfo from './components/PatientInfo.vue'
import Capturer from './components/Capturer.vue'
import Heatmap from './components/Heatmap.vue'
import Timeline from './components/Timeline.vue'
import Scatter from './components/Scatter.vue'
import clusters from "./assets/clusters.json";
import Notes from "./assets/Notes.json";
import convert from "./assets/conversion.json";
import * as d3 from "d3";
import categories from './assets/cat_16961_df.json'

export default {
  name: 'App',
  components: {
    PatientInfo,
    Capturer,
    Heatmap, 
    Timeline, 
    Scatter
  },
  data (){
    return{
      clustersNotes: [], //all clusters
      notes: [], // all notes
      notes_to_child: [], // notes to pass to the views
      clustersNotes_to_child: [], //clusters to pass to the views
      departments: [], // all departments present
      checkedBoxesSpecialism: [], // which check boxes are checked in specialism filter
      checkedBoxesType: ["Check-ups", "Admission"], //check box types for cluster type filter
      data_changed: 0, //number changes if something changes 
      search: "", // search term
      search_text: false, //if the yellow marking should be displayed
      search_tmp: "", //temporary place holder searched terms directly from search bar
      display_notes: false, //display the notes on the side
      note_id_to_display: -1, //which notes should be displayed on the side
      remove_cluster: [], //clusters that are removed due to filtering
      timeline_time_filter: [],
      scatter_filter: 'no_filter',
      scatter_high: [],
      scatter_brush_selection: 'no_selection',
      aggregated: true,
      highlight: null,
    }
  },
  methods: {
    //filtering the notes based on specialism or/and cluster type
    //filter_type is either specialism of cluster type
    //removed is which option should be removed, e.g. Check-ups
    filterNotes(filter_type, removed) {
      let tmp = [];
      if (filter_type == "Specialism") {
        //filter notes based on specialisms
        for (let i = 0; i < this.checkedBoxesSpecialism.length; i++) {
          let result = this.notes.Notes.filter((note) =>
            note.department.includes(this.checkedBoxesSpecialism[i])
          );
          for (let x of result) {
            tmp.push(x);
          }
        }
        this.notes_to_child = { Notes: tmp };
        //check if a cluster (dis)appears due to filtering > if cluster only has the filtered department(s)
        let filtered_out_dep = this.departments.filter(
          (value) => !this.checkedBoxesSpecialism.includes(value)
        );
        if (this.clustersNotes.clusters.length) {
          //find cluster id that needs to be removed or added
          for (let i = 0; i < this.clustersNotes.clusters.length; i++) {
            //if cluster contains only one department and that is part of the removed departments
            if (this.clustersNotes.clusters[i].department.length == 1) {
              if (
                this.clustersNotes.clusters[i].department[0] == removed &&
                !this.remove_cluster.includes(this.clustersNotes.clusters[i].id)
              ) {
                this.remove_cluster.push(this.clustersNotes.clusters[i].id);
              }
            }
            //if cluster is removed due to a combination of filtered out deparments
            if (
              this.clustersNotes.clusters[i].department.length <=
              filtered_out_dep.length
            ) {
              let push_to_remove = true;
              for (
                let j = 0;
                j < this.clustersNotes.clusters[i].department.length;
                j++
              ) {
                if (
                  !filtered_out_dep.includes(
                    this.clustersNotes.clusters[i].department[j]
                  )
                ) {
                  push_to_remove = false;
                }
              }
              if (
                push_to_remove &&
                !this.remove_cluster.includes(this.clustersNotes.clusters[i].id)
              ) {
                this.remove_cluster.push(this.clustersNotes.clusters[i].id);
              }
            }
          }
          if (
            this.remove_cluster.length > 0 &&
            this.checkedBoxesSpecialism.includes(removed) == false
          ) {
            //remove them
            for (let i = 0; i < this.remove_cluster.length; i++) {
              let tmp_filter = this.clustersNotes_to_child.clusters.filter(
                (cluster) => cluster.id != this.remove_cluster[i]
              );
              this.clustersNotes_to_child = { clusters: tmp_filter };
            }
          } else if (this.remove_cluster.length > 0) {
            //add a cluster
            let added_ids = [];
            for (let i = 0; i < this.remove_cluster.length; i++) {
              let push_to_add = false;
              let cluster_to_check = this.clustersNotes.clusters.filter(
                (cluster) => cluster.id == this.remove_cluster[i]
              ); //gives array back with one cluster in it
              for (let j = 0; j < cluster_to_check[0].department.length; j++) {
                if (
                  this.checkedBoxesSpecialism.includes(
                    cluster_to_check[0].department[j]
                  )
                ) {
                  push_to_add = true;
                  break;
                }
              }
              if (push_to_add) {
                this.clustersNotes_to_child.clusters.push(cluster_to_check[0]);
                added_ids.push(cluster_to_check[0].id);
              }
            }
            this.remove_cluster = this.remove_cluster.filter(
              (value) => !added_ids.includes(value)
            );
          }
        }
      } else if (filter_type == "Type") {
        //filter based on cluster type
        for (let i = 0; i < this.checkedBoxesType.length; i++) {
          let result = this.clustersNotes.clusters.filter(
            (cluster) => cluster.title == this.checkedBoxesType[i]
          );
          for (let x of result) {
            tmp.push(x);
          }
        }
        this.clustersNotes_to_child = { clusters: tmp };
        // also check specialism filters 
        this.filterNotes("Specialism");
      }
      this.data_changed += 1; //data changed so push to children (different views)
      if (this.clustersNotes_to_child.clusters) {
        //sort the cluster data
        this.clustersNotes_to_child.clusters.sort(function(a, b) {
          return a.id - b.id;
        });
      }
      if (this.notes_to_child.Notes) {
        //sort the note data
        this.notes_to_child.Notes.sort(function(a, b) {
          return a.id - b.id;
        });
      }
    },
    //search for terms
    search_term() {
      console.log(this.search_tmp);
      //reset the previous search
      this.search = this.search_tmp;
      this.search_text = true;     
    },
    //reset search
    remove_search() {
      this.search_text = false;
      this.search = "";
      document.getElementById("search").value = "";
    }, 
    add_note(note){
      this.notes.Notes.push(note);
      this.filterNotes('Specialism');
    },
    filter_time(stop, start){
      let note_ids = [];
      let cluster_names = [];
      for(let i=0; i < this.clustersNotes_to_child.clusters.length; i++){
        if(i >= stop && i <= start){
          cluster_names.push(this.clustersNotes_to_child.clusters[this.clustersNotes_to_child.clusters.length - i -1].name);
        }
      }
      for(let i=0; i<this.notes_to_child.Notes.length; i++){
        if(cluster_names.includes(this.notes_to_child.Notes[i].cluster)){
          note_ids.push(convert[this.notes_to_child.Notes[i].id]);
        }
      }
      this.timeline_time_filter = note_ids;
    },
    filter_time_remove(){
      this.timeline_time_filter = 'no_filter';
      this.scatter_filter = 'no_filter';
    },
    scatter_filter_time(set){
      this.scatter_filter = Array.from(set);
      console.log(this.scatter_filter);
    },
    scatter_highlight(a){
      console.log(a);
      d3.selectAll("circle").attr("class", "non_brushed");
      if(a != 'no_high'){
        d3.selectAll("circle").filter(function (d){
          return a.includes(d.concept);
        })
        .attr("class", "brushed");
      }      
    },
    scatter_select(a){
      let concepts;
      if(a != 'no_selection'){
        if(this.aggregated){
          let tmp = [];
          concepts = new Set();
          for(let i=0; i< a.length; i++){
            tmp.push(Object.keys(categories['concept']).find(key => categories['concept'][key] === a[i]));
          } 
          for(let i=0; i< tmp.length; i++){
            concepts.add(categories['category'][tmp[i]]);
          } 
          concepts = Array.from(concepts);   
        } else {
          concepts = a;
        }
        console.log(concepts);
        d3.selectAll('.cell').attr("class", "cell not-selected");
        d3.selectAll('.cell').filter(function (d){
              return (concepts.includes(d.concepta) || concepts.includes(d.conceptb));
          })
          .attr("class", "cell selected"); 
      } else {
        d3.selectAll('.cell').attr("class", "cell");
      }
    },
    heatmap_aggr(val){
      this.aggregated = val;
    }, 
    highlight_notes(val){
      console.log(val);
      this.highlight = val;
      this.data_changed += 1;
    },
    save_axis_labels(label){
      let str = document.getElementById('cap').value;
      if(str.charAt(str.length-1) == '.'){
        document.getElementById('cap').value += "\n\n Saved diseases, drugs and treatment concepts of interest: \n" + label;
      }
      else {
        document.getElementById('cap').value += "\n " + label;
      }
    }
  },
  created() {
    this.clustersNotes = clusters;
    this.notes = Notes;
    //get all the different departments in the notes
    let departments = new Set();
    for (let note of this.notes.Notes) {
      for (let department of note.department) {
        departments.add(department);
      }
    }
    this.departments = Array.from(departments);
    this.checkedBoxesSpecialism = this.departments;
    this.filterNotes("Specialism"); // fill filtered note array on creation
    this.filterNotes("Type");
  },
}
</script>

<style lang="scss">
.selected{
  opacity: 1;
}

.not-selected{
  opacity: 0.5;
}



#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--lightest-grey);
  width: 100vw;
  font-size: 13px;
}

.fourth-height{
  height: 25vh;
}

.threefourth-height{
  height: 75vh;
}

.border_side_bottom {
  border-style: none solid solid none;
  border-width: thin;
  border-color: #474745; 
}

.border_bottom {
  border-style: none none solid none;
  border-width: thin;
  border-color: #474745; 
}

.padding_normal {
  padding: 1rem 0.5rem 1rem 1.75rem !important;
}

.scroll {
  overflow-y: scroll;
}
.scroll::-webkit-scrollbar {
  -webkit-appearance: none;
}
.scroll::-webkit-scrollbar:vertical {
  width: 11px;
}
.scroll::-webkit-scrollbar:horizontal {
  height: 11px;
}
.scroll::-webkit-scrollbar-thumb {
  border-radius: 8px;
  border: 2px solid var(--lightest-grey); /* should match background, can't be transparent */
  background-color: var(--dark-grey);
}

.max_height_width {
  height: 90%;
  width: 100%;
}

.header {
  color: var(--darkest-grey);
  font-size: large;
  font-weight: bold;
}



.hidden {
  display: none !important;
}

.height_inherit {
  height: inherit;
}
.height_two_fifth {
  height: 50vh;
}
.height_one_fifth {
  height: 20vh;
}
.scroll {
  overflow-y: scroll;
}
.scroll::-webkit-scrollbar {
  -webkit-appearance: none;
}
.scroll::-webkit-scrollbar:vertical {
  width: 11px;
}
.scroll::-webkit-scrollbar:horizontal {
  height: 11px;
}
.scroll::-webkit-scrollbar-thumb {
  border-radius: 8px;
  border: 2px solid var(--lightest-grey); /* should match background, can't be transparent */
  background-color: var(--dark-grey);
}
.padding_normal {
  padding: 1rem 0.5rem 1rem 1.75rem !important;
}
.max_height_width {
  height: 90%;
  width: 100%;
}

.bold {
  font-weight: bold;
}
.display_flex {
  display: flex;
}
.margin_left_normal {
  margin-left: 1rem;
}
.table_padding_left {
  padding-left: 0.5rem;
}
th {
  font-weight: normal;
}
.input {
  border-color: var(--darkest-grey) !important;
  color: var(--dark-grey) !important;
  border-radius: 8px !important;
}
.button_style {
  background-color: var(--dark-grey) !important;
  color: var(--lightest-grey) !important;
  border-radius: 12px !important;
  border: none !important;
  height: 2em !important;
  margin-top: 0.5rem !important;
  font-size: 12px !important;
}
.button_note {
  width: 80px;
  margin: 0.2rem 0.2rem 0.2rem 0 !important;
}
.sub_header {
  font-size: 16px !important;
  margin-top: 0.5rem !important;
}
label.is-checkbox {
  border: none;
  color: var(--darkest-grey);
  white-space: nowrap;
  display: inline-flex;
  justify-content: center;
  margin-top: 0.5rem;
  cursor: pointer;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
  .checkmark {
    color: transparent;
    position: relative;
    i {
      z-index: 1;
    }
    &:before {
      content: "";
      position: absolute;
      right: 0;
      left: 0;
      top: 0;
      bottom: 0;
      z-index: 0;
      border-radius: 8px;
      border: 3px solid var(--grey);
    }
  }
  .is-blue {
    &:before {
      border: 3px solid var(--blue) !important;
    }
  }
  .is-red {
    &:before {
      border: 3px solid var(--red) !important;
    }
  }
  .is-orange {
    &:before {
      border: 3px solid var(--orange) !important;
    }
  }
  .is-green {
    &:before {
      border: 3px solid var(--green-button) !important;
    }
  }
  input[type="checkbox"] {
    position: absolute;
    visibility: hidden;
    cursor: pointer;
    &:checked ~ .checkmark {
      color: var(--lightest-grey);
      background-color: var(--grey);
      border-radius: 8px;
      .blue-background {
        background-color: var(--blue) !important;
        border-radius: 8px;
        color: var(--lightest-grey);
      }
      .red-background {
        background-color: var(--red) !important;
        border-radius: 8px;
        color: var(--lightest-grey);
      }
      .orange-background {
        background-color: var(--orange) !important;
        border-radius: 8px;
        color: var(--lightest-grey);
      }
      .green-background {
        background-color: var(--green) !important;
        border-radius: 8px;
        color: var(--lightest-grey);
      }
    }
  }
  .svg-inline--fa.fa-w-16 {
    width: 1.5em;
  }
  .svg-inline--fa {
    height: 1.2em;
  }
  .icon {
    & {
      height: 1.5em;
      width: 1.5em;
      margin-right: 0.35em;
    }
  }
}
</style>
