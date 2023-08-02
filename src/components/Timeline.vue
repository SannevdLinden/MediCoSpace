<template>
  <div>
    <div class="columns height_inherit">      
      <div class="column is-12" style="padding-top:0.2rem; padding-left: 2rem;">
        <p id='filter_time' style='opacity:0%'>
      Delete current time filter
      <button
      v-on:click="filter_remove"
      class="delete"
      style="margin-left:0.5rem"
    >      
    </button>
    </p>
    <p id='high_time' style='opacity:0%'> 
      <span id='high_time_text'></span>
      <button
      v-on:click="high_remove"
      class="delete"
      style="margin-left:0.5rem"
    >      
    </button>
    </p>
        <div class="columns height_90" id="container">
          <div class="column scroll" style="margin-top:0.75rem">
            <div class="columns">
              <!-- timeline-->
              <div
                class="column is-2"
                v-bind:class="{ 'is-3': display_notes }"
                style="padding-right: 0px !important"
              >
                <div
                  style="position: relative; z-index: 2; height: 0px;"
                  id="connect_box_bar"
                ></div>
                <div id="timeline"></div>
                <div id="brush_time" style='position: relative; z-index: 3;'></div>
              </div>
              <!-- list with clusters of notes-->
              <div
                class="column  full_height"
                style="padding-left: 0px !important"
              >
                <div id="clusters_height">
                  <div
                    v-bind:key="cluster.id"
                    v-for="(cluster, index) in clustersNotes.clusters"
                  >
                    <Cluster
                      v-bind:cluster="[
                        cluster,
                        clusterNoteButtons[index],
                        search_text,
                        search,
                        highlight
                      ]"
                      v-on:open-note="noteOpen"
                      v-on:highlight-word="highlight_words"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
          <!-- List with the note texts to display on the side-->
          <div class="column is-5" v-bind:class="{ hidden: !display_notes }">
            <button v-on:click="hideNotes" class="button button_style">
              Back
            </button>
            <NotesList
              v-bind:notes_id_display="[
                notes_id_display,
                search_text,
                search,
                highlight
              ]"              
              v-on:notes-loaded="makeTimeline"              
              style="margin-top:0.5rem"
            />
          </div>
        </div>
      </div>
    </div>
    
  </div>
</template>

<script>
import * as d3 from "d3";
import Cluster from "../components/Cluster.vue";
import NotesList from "../components/Notes.vue";
import conversion from '../assets/conversion.json';

export default {
  name: 'Timeline',
  props: ["data_to_child"],
  components: {
    Cluster,
    NotesList
  },
  data() {
    return {
      clustersNotes: [], //all clusters
      reversedNotes: [], //all notes from newest to oldest 
      notes: [], // all notes
      clusterNoteButtons: [], ////grey note buttons in the cluster per cluster
      display_notes: false, //display notes on side
      notes_id_display: [], //[id note, [notes in this cluster], word for highlight] select notes to display on side and
      //which note button was pushed (id note)      
      highlighted_word: "", //default highlighted word
      search_text: false, //if a search is executed
      search: "", //searched term
      stripe_background: { //color stripes connecting vertical bars on the timeline with the clusters
        borderColor: "var(--dark-grey)",
      },
      scroll_to_cluster: -1, //scroll to correct cluster on timeline
      prev_opened_clus: -1, //previous opened cluster to read the notes
      cluster_stop: null,
      cluster_start: null, // time filter
      filter_text: false,
      highlight: null
    };
  },
  methods: {
    //open notes on the side and scroll the the note with id='id'
    noteOpen(id) {
      this.display_notes = true;
      // send only the notes that need to be displayed to NotesList component
      let notes_id_display = [id];
      let cluster_name = this.notes.Notes.filter((note) => note.id == id);
      cluster_name = cluster_name[0].cluster;
      let tmp = this.notes.Notes.filter((note) => note.cluster == cluster_name);
      notes_id_display.push(tmp);
      notes_id_display.push(this.highlighted_word);
      this.notes_id_display = notes_id_display;
      let cluster_id = this.clustersNotes.clusters.filter(
        (cluster) => cluster.name == cluster_name
      );
      //change background color of opened previous cluster back and 
      //change color of currently opened cluster to darker background
      if (
        this.prev_opened_clus > -1 &&
        this.prev_opened_clus != cluster_id[0].id
      ) {
        const prev_elmnt = document.getElementById(
          "cluster_" + String(this.prev_opened_clus)
        );
        if (prev_elmnt.style.backgroundColor == "var(--blue-opac-mid)") {
          prev_elmnt.style.backgroundColor = "var(--blue-opac)";
        } else if (
          prev_elmnt.style.backgroundColor == "var(--orange-opac-mid)"
        ) {
          prev_elmnt.style.backgroundColor = "var(--orange-opac)";
        }
      }
      const elmnt = document.getElementById(
        "cluster_" + String(cluster_id[0].id)
      );
      if (elmnt.style.backgroundColor == "var(--blue-opac)") {
        elmnt.style.backgroundColor = "var(--blue-opac-mid)";
      } else if (elmnt.style.backgroundColor == "var(--orange-opac)") {
        elmnt.style.backgroundColor = "var(--orange-opac-mid)";
      }
      this.prev_opened_clus = cluster_id[0].id;
      //scroll to the correct cluster and note
      if (elmnt) {
        setTimeout(() => elmnt.scrollIntoView(), 100);
      }
      setTimeout(() => this.scrollToNote(id), 100);
    },
    //scroll to the correct note
    scrollToNote(id) {
      const elmnt_note = document.getElementById(String(id));
      elmnt_note.scrollIntoView();
    },
    //hide the notes on the side
    hideNotes() {
      this.display_notes = false;
      const elmnt = document.getElementById(
        "cluster_" + String(this.prev_opened_clus)
      );
      if (elmnt) {
        setTimeout(() => elmnt.scrollIntoView(), 100);
      }
      const prev_elmnt = document.getElementById(
        "cluster_" + String(this.prev_opened_clus)
      );
      if (prev_elmnt.style.backgroundColor == "var(--blue-opac-mid)") {
        prev_elmnt.style.backgroundColor = "var(--blue-opac)";
      } else if (prev_elmnt.style.backgroundColor == "var(--orange-opac-mid)") {
        prev_elmnt.style.backgroundColor = "var(--orange-opac)";
      }
      if (this.clustersNotes.clusters.length > 0) {
        setTimeout(() => this.makeTimeline(), 100); //small delay to make sure html is loaded
      }
    },   
     //if user clicks on word in word summaries open or close the notes on the side
    highlight_words(word_info) {
      let id = word_info[1];
      let word = word_info[0];
      if (word_info[2] % 2 == 0) {
        this.highlighted_word = word;
        this.noteOpen(id);
      } else {
        this.highlighted_word = "";
        this.hideNotes();
        this.notes_id_display[2] = "";
      }
    },
    //reverse the order of array based on the stop_date of the clusters or the date of the note
    //from newest to oldest
    reverse(data) {
      data.sort(function(a, b) {
        a = a.date_stop.split("-");
        a = new Date(a[2], a[1] - 1, a[0]);
        a = a.getTime();
        b = b.date_stop.split("-");
        b = new Date(b[2], b[1] - 1, b[0]);
        b = b.getTime();
        return b - a;
      });
      return data;
    },
    //if window is resized recalculate the timeline
    windows_size() {
      if(document.getElementById("timeline")){
        console.log("WINDOW RESIZE");
        this.makeTimeline();
      }
    },
    //calculate the timeline
    makeTimeline() {
      let innerHeight = document.getElementById("clusters_height").offsetHeight; //height of all clusters
      let timeline = document.getElementById("timeline"); //timeline div
      let connect_box_bar = document.getElementById("connect_box_bar"); //element that connect vertical bars on timeline with cluster boxes
      let total_days = 0; //total amount of days that are drawn on the timeline (not the skip intervals, dashed timeline parts)
      let intervals = []; //[duration of cluster in days, start, stop] per cluster
      let skip_differences = []; //in days the difference in time between consecutive clusters, negative means overlap
      let height_skip = 0; //height of a skip interval/dashed timeline part 
      let height_day = 0; //height of a day
      let month = [
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
      ];
      timeline.innerHTML = "";
      connect_box_bar.innerHTML = "";
      //timeline is always minimal 85vh
      if (innerHeight < document.getElementById("container").offsetHeight) {
        innerHeight = document.getElementById("container").offsetHeight;
      }
      
      for (let i = 0; i < this.clustersNotes.clusters.length; i++) {
        //fill intervals
        let tmp = this.clustersNotes.clusters[i];
        let start = tmp.date_start.split("-");
        let stop = tmp.date_stop.split("-");
        start = new Date(start[2], start[1] - 1, start[0]); //month start counting at 0
        stop = new Date(stop[2], stop[1] - 1, stop[0]);
        let difference = Math.round(
          (stop.getTime() - start.getTime()) / (1000 * 3600 * 24)
        );
        //the max length of a cluster bar on timeline is that of the length of 15 days
        if (difference + 1 > 15) {
          total_days += 15;
        } else {
          total_days += difference + 1; // from 16th to 17th is 1 day difference but 2 days in total
        }
        intervals.push([difference + 1, start, stop]);
      }
      //fill skip differences
      for (let i = 0; i < intervals.length; i++) {
        //start cluster (i-1) - stop cluster i in days
        if (i != 0) {
          let tmp = Math.round(
            (intervals[i - 1][1].getTime() - intervals[i][2].getTime()) /
              (1000 * 3600 * 24)
          );
          if (tmp < 0) {
            //same day should also count as overlap
            tmp--;
          } else {
            tmp++;
          }
          if (tmp < 0) {
            skip_differences.push(tmp); //for overlap days themselves should count
          } else {
            skip_differences.push(tmp - 2); //do not count the days themselves
          }
        }
      }
      
      for (let i = 0; i < skip_differences.length; i++) {
        if (skip_differences[i] <= 3 && skip_differences[i] > 0) {
          //if difference between to clusters is less than 3 days and no overlap do not draw dashed line
          total_days += skip_differences[i];
        } else if (skip_differences[i] < 0) {
          //if there is overlap with previous cluster subtract this from total days
          if (Math.abs(skip_differences[i]) > intervals[i + 1][0]) {
            if (intervals[i + 1][0] > 15) {
              total_days -= 15;
            } else {
              total_days -= intervals[i + 1][0];
            }
          } 
        }
      }
      //calc height of day and skip height
      height_day = (innerHeight * 0.8) / total_days; //80% for the intervals
      //min day height
      if (height_day < 10) {
        height_day = 10;
      }
      let count_skip = 0;
      if (skip_differences.length > 0) {
        // check which intevals are bigger than 3 to see how many skip part to get
        for (let i = 0; i < skip_differences.length; i++) {
          if (skip_differences[i] > 3) {
            count_skip++;
          }
        }
        height_skip = (innerHeight * 0.2) / count_skip;
        // min skip height
        if (height_skip < 100) {
          height_skip = 100;
        }
      }
      let width_timeline = document.getElementById("timeline").offsetWidth;
      let width_bars = Math.floor(0.6 * width_timeline - 20); //65% width for all the bars - 20px for the timeline
      let number_overlap = 0; //max number of clusters that overlap
      for (let i = 0; i < skip_differences.length; i++) {
        if (skip_differences[i] < 0) {
          if (number_overlap > 0) {
            if (skip_differences[i - 1] < 0) {
              number_overlap++;
            } else {
              number_overlap = 1;
            }
          }
          number_overlap++;
        }
      }
      //if there are too many overlapping bars that it does not fit anymore make bars timeline thinner and padding less
      if (number_overlap * 10 < width_bars) {
        width_bars = 5;
      } else if (number_overlap * 4 < width_bars) {
        width_bars = 2;
      } else {        
        width_bars = 1;
      }
      
      //make the indications (start date, horizotnal grey bar, stop date) for the amount of time that is skipped in the skip parts
      let skip_indication_area = Math.floor(0.5 * width_timeline); // space for indication
      let skip_indication_lenght =
        skip_indication_area / Math.max(...skip_differences); // what the width of the horizontal grey bar should be 
      let html_skip_dif = []; //html parts of all skip differences
      let min_indication_lenght = 5; //min width grey horizontal bar
      let text_skip_indicator = "";
      for (let i = 0; i < skip_differences.length; i++) {
        if (skip_differences[i] <= 3) { //no skip difference part
          html_skip_dif.push("nothing to display");
        } else {
          let width_indication = skip_indication_lenght * skip_differences[i]; //calc width of the grey horizontal bar based on #days
          if (width_indication < min_indication_lenght) {
            width_indication = min_indication_lenght;
          }
          let year = this.$moment(intervals[i][1]).diff(
            intervals[i + 1][2],
            "years"
          ); //calc amount of year in skip difference
          let month = this.$moment(intervals[i][1]).diff(
            intervals[i + 1][2],
            "months"
          );
          month = month - 12 * year; //calc amount of months in skip difference
          let day = this.$moment(intervals[i + 1][2]).add(year, "years");
          day = this.$moment(day).add(month, "months");
          day = this.$moment(intervals[i][1]).diff(day, "days");
          //format of the text under the grey horizontal bar
          if (year < 1) {
            text_skip_indicator = month + "m " + day + "d";
          } else {
            text_skip_indicator = year + "y " + month + "m";
          }
          //total html part for one skip difference
          let tmp_html =
            "<div class='display_flex' style='margin-top:" +
            0.1 * height_skip +
            "px; margin-left: 10px; width:100%;'><div class='small_vertical_bar'></div><div style='width:" +
            width_indication +
            "px; height:5px; background-color:#bbb;'></div></div><span style='font-style: italic; font-size: 10px; margin-left: 10px;'>" +
            text_skip_indicator +
            "</span>";
          html_skip_dif.push(tmp_html);
        }
      }

      //draw timeline
      let html_code = "";
      for (let i = 0; i < intervals.length; i++) {
        let j = i; //if there is overlap between intervals the height of the grey solid timeline piece need to be recalculated
        let height_cluster_bar = intervals[i][0] * height_day; 
        if (intervals[i][0] > 15) {
          height_cluster_bar = 15 * height_day;
        }
        let height_timeline_part = height_cluster_bar;
        let stop = intervals[i][1];
        let result = intervals[i][0];
        if (intervals[i][0] > 15) {
          result = 15;
        }
        //check which intervals overlap with the current one
        while (skip_differences[j] < 0 && j < skip_differences.length) {
          let tmp_stop = intervals[j + 1][1];
          if (tmp_stop < stop) {
            //if the overlapping bars begins earlier the timeline part should be take this extra length in account
            stop = tmp_stop;
            let len_current_bar = intervals[j + 1][0];
            if (len_current_bar > 15) {
              len_current_bar = 15;
            }
            //if two overlapping bars both exceed the max length and the first bar is completely overlapping the second the height of the second
            // needs to be recalculated. Otherwise the second bar stops later on the timeline because they both have max length while in time this is not the case 
            if (len_current_bar == 15 && intervals[i][0] > 15) {
              result +=
                15 - (Math.abs(skip_differences[j]) / intervals[i][0]) * 15;
            } else {
              result += len_current_bar + skip_differences[j];
            }
          }
          j++;
        }
        if (stop != intervals[i][1]) {
          //partial overlap
          height_timeline_part = result * height_day;
        }
        // check which color is needed
        // if (this.clustersNotes.clusters[i].name.includes("check_up")) {
        //   this.stripe_background.borderColor = "var(--blue)";
        // } else if (this.clustersNotes.clusters[i].name.includes("admis")) {
        //   this.stripe_background.borderColor = "var(--orange)";
        // }
        if (i == 0) {
          //first timeline part and first bar with special top margin
          html_code +=
            "<div class='display_flex' id='part" + i + "'><div class='vl5 ' style='height:" +
            height_timeline_part +
            "px;'></div> <div class='vl" +
            width_bars +
            " margin-side-small" +
            width_bars +
            "' style='height:" +
            height_cluster_bar +
            "px; margin-left:0px; border-color:" +
            this.stripe_background.borderColor +
            "' id='bar" +
            i +
            "'></div>";
        } else {
          if (
            skip_differences[i - 1] < 0 &&
            intervals[i - 1][0] > 15 &&
            intervals[i][0] > 15 &&
            intervals[i - 1][1] < intervals[i][1]
          ) {
            height_cluster_bar =
              (intervals[i][0] / intervals[i - 1][0]) * 15 * height_day;
          }
          //timeline skip parts
          if (skip_differences[i - 1] <= 3 && skip_differences[i - 1] >= 0) {
            //if there should not be a skip interval but no overlap
            let height_non_dash = skip_differences[i - 1] * height_day;
            if (height_non_dash == 0) {
              height_non_dash = 5;
            }
            html_code += "</div>"; //first close the flex div from previous bars
            html_code +=
              "<div class='vl5' style='height:" +
              height_non_dash +
              "px' id='part" + i + "5'></div>";
          } else if (skip_differences[i - 1] > 3) {
            //there is no overlap between intervals
            html_code += "</div>"; //first close the flex div from previous bars
            html_code +=
              "<div class='display_flex skip_part'><div class='vl-dashed5' style='height:" +
              height_skip +
              "px'></div><div style='position: relative; margin-left: 5px;'><span style='font-style: italic; font-size: 10px'>" +
              intervals[i - 1][1].getDate() +
              " " +
              month[intervals[i - 1][1].getMonth()] +
              " " +
              intervals[i - 1][1].getFullYear() +
              "</span><br>" +
              html_skip_dif[i - 1] +
              "<br><span style='font-style: italic; font-size: 10px; position: absolute; bottom:0px'>" +
              intervals[i][2].getDate() +
              " " +
              month[intervals[i][2].getMonth()] +
              " " +
              intervals[i][2].getFullYear() +
              "</span></div></div>";
          }
          let same_start_comp = 0; //if they have the same stop date let the second one start a bit later
          if (intervals[i][2].getTime() == intervals[i - 1][2].getTime()) {
            same_start_comp = 8;
          }
          //if there is overlap calc the margin to the top to place the timeline piece in correct position
          let overlap_max_length_top_margin =
            intervals[i - 1][0] - Math.abs(skip_differences[i - 1]); //difference in top margin if there is overlap
          if (intervals[i - 1][0] > 15) {
            //if there is overlap with a bar off max length margin needs to be recalculated
            overlap_max_length_top_margin =
              (overlap_max_length_top_margin / intervals[i - 1][0]) * 15;
            if (overlap_max_length_top_margin < 8 / height_day) {
              //make sure horizontal bars do not overlap
              overlap_max_length_top_margin = 8 / height_day;
            }
          }
          //also take the top margin from other earlier overlapping intervals that also overlap with the current one into account
          let k = i - 2;
          if (skip_differences[i - 1] < 0) {
            while (skip_differences[k] < 0 && k > 0) {
              let tmp = intervals[k][0] - Math.abs(skip_differences[k]); //difference in top margin if there is overlap
              if (intervals[k][0] > 15) {
                //if there is overlap with a bar off max length margin needs to be recalculated
                tmp = (tmp / intervals[k][0]) * 15;
              }
              overlap_max_length_top_margin += tmp;
              k--;
            }
          }
          if (i == intervals.length - 1) {
            //last timeline bar with special bottom margin
            if (skip_differences[i - 1] < 0) {
              // overlap
              html_code +=
                "<div class='vl" +
                width_bars +
                " margin-side-small" +
                width_bars +
                " margin-bottom-line' style='height:" +
                (height_cluster_bar - (8 + same_start_comp)) +
                "px; margin-top:" +
                (overlap_max_length_top_margin * height_day + same_start_comp) +
                "px !important; border-color:" +
                this.stripe_background.borderColor +
                "' id='bar" +
                i +
                "'></div></div>";
            } else {
              //no overlap
              html_code +=
                "<div class='display_flex' id='part" + i + "'><div class='vl5' style='height:" +
                height_timeline_part +
                "px'></div><div class='vl" +
                width_bars +
                " margin-side-small" +
                width_bars +
                " margin-bottom-line' style='height:" +
                height_cluster_bar +
                "px; border-color:" +
                this.stripe_background.borderColor +
                "' id='bar" +
                i +
                "'></div></div>";
            }
          } else {
            //solid timeline parts and bars
            if (skip_differences[i - 1] < 0) {
              //overlapping bars
              html_code +=
                "<div class='vl" +
                width_bars +
                " margin-side-small" +
                width_bars +
                "' style='height:" +
                (height_cluster_bar - same_start_comp) +
                "px; margin-top:" +
                (overlap_max_length_top_margin * height_day + same_start_comp) +
                "px !important; border-color:" +
                this.stripe_background.borderColor +
                "' id='bar" +
                i +
                "'></div>";
            } else {
              // not overlap
              html_code +=
                "<div class='display_flex' id='part" + i + "'><div class='vl5' style='height:" +
                height_timeline_part +
                "px'></div><div class='vl" +
                width_bars +
                "  margin-side-small" +
                width_bars +
                "' style='height:" +
                height_cluster_bar +
                "px; border-color:" +
                this.stripe_background.borderColor +
                "' id='bar" +
                i +
                "'></div>";
            }
          }
        }
      }
      timeline.innerHTML +=
        "<div class='display_flex'><div class='dot'></div><div style='font-style: italic; font-size: 10px; margin-left:5px;'>" +
        intervals[0][1].getDate() +
        " " +
        month[intervals[0][1].getMonth()] +
        " " +
        intervals[0][1].getFullYear() +
        "</div></div>"; //start dot
      timeline.innerHTML += html_code; //the timeline
      timeline.innerHTML +=
        "<div class='display_flex' style='margin-top:-8px;'><div class='dot'></div><div style='font-style: italic; font-size: 10px; margin-left:5px;'>" +
        intervals[intervals.length - 1][2].getDate() +
        " " +
        month[intervals[intervals.length - 1][2].getMonth()] +
        " " +
        intervals[intervals.length - 1][2].getFullYear() +
        "</div></div>"; //final dot
      //draw the horizontal and diagonal colored bars to connect the timeline pieces with the cluster boxes
      //set the height of the div overlaying the timeline to the height of the timeline and
      //set the margin of the timeline in such a way that they are aligned
      let height_timeline = timeline.offsetHeight;
      connect_box_bar.style.height = height_timeline + "px";
      timeline.style.marginTop = -1 * height_timeline + "px";
      //draw the connecting lines based on coordinates
      let coord_timeline = timeline.getBoundingClientRect();
      for (let i = 0; i < intervals.length; i++) {
        let number_cluster = this.clustersNotes.clusters[i].id;
        let coord_bar = document
          .getElementById("bar" + i)
          .getBoundingClientRect();
        let coord_cluster_stripe = document
          .getElementById("cluster_stripe" + number_cluster)
          .getBoundingClientRect();
        let margin_top = coord_bar.top - coord_timeline.top;
        let margin_left = coord_bar.left - coord_timeline.left;
        let width_stripe =
          coord_timeline.width - margin_left - 0.35 * width_timeline;
        let height_diagonal = Math.abs(
          coord_bar.top - coord_cluster_stripe.top
        );
        // check which color is needed
        // if (this.clustersNotes.clusters[i].name.includes("check_up")) {
        //   this.stripe_background.borderColor = "var(--blue)";
        // } else if (this.clustersNotes.clusters[i].name.includes("admis")) {
        //   this.stripe_background.borderColor = "var(--orange)";
        // }
        if (height_diagonal == 0) {
          //if the height of the stripe of the timeline bar is the same as the cluster
          connect_box_bar.innerHTML +=
            "<div class='bar_to_cluster_stripe' style='margin-top:" +
            margin_top +
            "px; width:" +
            width_stripe +
            "px; position: absolute; margin-left:" +
            margin_left +
            "px; background: " +
            this.stripe_background.borderColor +
            ";'></div> <div style='background: " +
            this.stripe_background.borderColor +
            "; position: absolute; height: 5px; width:" +
            0.35 * width_timeline +
            "px; margin-top:" +
            (coord_cluster_stripe.top - coord_timeline.top) +
            "px; margin-left: 65%;'></div>";
        } else if (coord_bar.top > coord_cluster_stripe.top) {
          //cluster stripe is closer to top than bar strip
          let diagonal =
            "background: linear-gradient(to top left, rgba(0,0,0,0) calc(50% - 2.5px), " +
            this.stripe_background.borderColor +
            ", rgba(0,0,0,0) calc(50% + 2.5px) );";
          connect_box_bar.innerHTML +=
            "<div class='bar_to_cluster_stripe' style='margin-top:" +
            margin_top +
            "px; width:" +
            width_stripe +
            "px; position: absolute; margin-left:" +
            margin_left +
            "px; background: " +
            this.stripe_background.borderColor +
            ";'></div> <div style='background: #bbb; position: absolute; height:" +
            (height_diagonal + 5) +
            "px; width:" +
            0.35 * width_timeline +
            "px; " +
            diagonal +
            " margin-top:" +
            (coord_cluster_stripe.top - coord_timeline.top) +
            "px; margin-left: 65%;'></div>";
        } else {
          //cluster stripe is further to top than bar strip
          let diagonal =
            "background: linear-gradient(to top right, rgba(0,0,0,0) calc(50% - 2.5px), " +
            this.stripe_background.borderColor +
            ", rgba(0,0,0,0) calc(50% + 2.5px) );";
          connect_box_bar.innerHTML +=
            "<div class='bar_to_cluster_stripe' style='margin-top:" +
            margin_top +
            "px; width:" +
            width_stripe +
            "px; position: absolute; margin-left:" +
            margin_left +
            "px; background: " +
            this.stripe_background.borderColor +
            ";'></div> <div style='background: #bbb; position: absolute; height:" +
            (height_diagonal + 5) +
            "px; width:" +
            0.35 * width_timeline +
            "px; " +
            diagonal +
            " margin-top:" +
            (coord_bar.top - coord_timeline.top) +
            "px; margin-left: 65%;'></div>";
        }
      }
      this.brush_time();
    },
    brush_time(){
      let height = document.getElementById('timeline').offsetHeight;
      let element = document.getElementById('brush_time');
      let method = this;
      element.style.marginTop = String(-1 * height) + 'px'; 
      var boxes = document.getElementsByClassName('cluster_box');
      for(let i = 0; i < boxes.length; i++){
          document.getElementById("cluster_" + i).style.opacity = '100%';
      }

      d3.select('#brush_time_svg').remove();

      var svg = d3.select('#brush_time').append("svg")
        .attr("width", 75)
        .attr("height", height) 
        .attr('id', 'brush_time_svg')
        .append("g");

      svg
      .call( d3.brushY() 
        .on('end', brushed)                      
        .extent( [ [0,0], [20,height] ] )             
      )

      let skip_height = document.getElementsByClassName('skip_part')[0].offsetHeight;
      let height_part0 = document.getElementById('part0').offsetHeight;
      let height_part1 = document.getElementById('part1').offsetHeight;
      let height_part2 = document.getElementById('part2').offsetHeight;
      let height_part3 = document.getElementById('part3').offsetHeight;
      let height_part5 = document.getElementById('part5').offsetHeight;
      let height_part6 = document.getElementById('part6').offsetHeight;
      let height_part75 = document.getElementById('part75').offsetHeight;
      let height_part7 = document.getElementById('part7').offsetHeight;
      let height_part85 = document.getElementById('part85').offsetHeight;
      let height_part8 = document.getElementById('part8').offsetHeight;
      let height_part95 = document.getElementById('part95').offsetHeight;
      let height_part9 = document.getElementById('part9').offsetHeight; 
      // let height_part10 = document.getElementById('part10').offsetHeight;
      
      function brushed(){
        method.filter_text = true;
        document.getElementById('filter_time').style.opacity= '100%';
        let height_brush = d3.brushSelection(this);
        let cluster_start = getCluster(height_brush[0], true);
        let cluster_stop =getCluster(height_brush[1], false);
        console.log(cluster_start);
        console.log(cluster_stop);
        var boxes = document.getElementsByClassName('cluster_box');
        for(let i = 0; i < boxes.length; i++) {
          boxes[i].style.opacity = '30%';
        }        
        for(let i = cluster_stop; i < cluster_start + 1; i++){
          document.getElementById("cluster_" + i).style.opacity = '100%';
        }
        // get notes belonging to clusters and give this to heatmap filter
        method.cluster_start = cluster_start;
        method.cluster_stop = cluster_stop;
      }

      function getCluster(h, start){
        if(start){
          if(h <= (height_part0 + 25)){
            return 10
          } else if (h > (height_part0 + 25) && h <= (height_part0 + 25 + skip_height + height_part1)){
            return 9
          } else if (h > (height_part0 + 25 + skip_height + height_part1) &&
            h <= (height_part0 + 25 + 2*skip_height + height_part1 + height_part2)){
            return 8
          } else if (h > (height_part0 + 25 + 2*skip_height + height_part1 + height_part2) &&
            h <= (height_part0 + 25 + 3*skip_height + height_part1 + height_part2 + height_part3)){
            return 7
          }  else if (h > (height_part0 + 25 + 3*skip_height + height_part1 + height_part2 + height_part3)
            && h <= (height_part0 + 25 + 4*skip_height + height_part1 + height_part2 + height_part3 + height_part5)){
            return 5
          } else if (h > (height_part0 + 25 + 4*skip_height + height_part1 + height_part2 + height_part3 + height_part5)
            && h <= (height_part0 + 25 + 5*skip_height + height_part1 + height_part2 + height_part3 + height_part5 + height_part6)){
            return 4
          } else if (h > (height_part0 + 25 + 5*skip_height + height_part1 + height_part2 + height_part3 + height_part5 + height_part6)
            && h <= (height_part0 + 25 + 5*skip_height + height_part1 + height_part2 + height_part3 + height_part5 + height_part6 + height_part75 + height_part7)){
            return 3
          } else if (h > (height_part0 + 25 + 5*skip_height + height_part1 + height_part2 + height_part3 + height_part5 + height_part6 + height_part75 + height_part7)
            && h <= (height_part0 + 25 + 5*skip_height + height_part1 + height_part2 + height_part3 + height_part5 + height_part6 + height_part75 + height_part7 +
              height_part85 + height_part8)){
            return 2
          } else if (h > (height_part0 + 25 + 5*skip_height + height_part1 + height_part2 + height_part3 + height_part5 + height_part6 + height_part75 + height_part7 +
              height_part85 + height_part8) && h <= (height_part0 + 25 + 5*skip_height + height_part1 + height_part2 + height_part3 + height_part5 + height_part6 + height_part75 + height_part7 +
              height_part85 + height_part8 + height_part95 + height_part9)){
            return 1
          } else if (h > (height_part0 + 25 + 5*skip_height + height_part1 + height_part2 + height_part3 + height_part5 + height_part6 + height_part75 + height_part7 +
              height_part85 + height_part8 + height_part95 + height_part9)){
            return 0
          }
        } else {
          if(h <= (height_part0 + 25 + skip_height)){
            return 10
          } else if (h > (height_part0 + 25 + skip_height) && h <= (height_part0 + 25 + 2*skip_height + height_part1)){
            return 9
          } else if (h > (height_part0 + 25 + 2*skip_height + height_part1) &&
            h <= (height_part0 + 25 + 3*skip_height + height_part1 + height_part2)){
            return 8
          } else if (h > (height_part0 + 25 + 3*skip_height + height_part1 + height_part2) &&
            h <= (height_part0 + 25 + 4*skip_height + height_part1 + height_part2 + height_part3)){
            return 6
          }  else if (h > (height_part0 + 25 + 4*skip_height + height_part1 + height_part2 + height_part3)
            && h <= (height_part0 + 25 + 5*skip_height + height_part1 + height_part2 + height_part3 + height_part5)){
            return 5
          } else if (h > (height_part0 + 25 + 5*skip_height + height_part1 + height_part2 + height_part3 + height_part5)
            && h <= (height_part0 + 25 + 5*skip_height + height_part1 + height_part2 + height_part3 + height_part5 + height_part6 + height_part75)){
            return 4
          } else if (h > (height_part0 + 25 + 5*skip_height + height_part1 + height_part2 + height_part3 + height_part5 + height_part6 + height_part75)
            && h <= (height_part0 + 25 + 5*skip_height + height_part1 + height_part2 + height_part3 + height_part5 + height_part6 + height_part75 
              + height_part7 + height_part85)){
            return 3
          } else if (h > (height_part0 + 25 + 5*skip_height + height_part1 + height_part2 + height_part3 + height_part5 + height_part6 + height_part75 + height_part7 + height_part85)
            && h <= (height_part0 + 25 + 5*skip_height + height_part1 + height_part2 + height_part3 + height_part5 + height_part6 + height_part75 + height_part7 +
              height_part85 + height_part8 + height_part95)){
            return 2
          } else if (h > (height_part0 + 25 + 5*skip_height + height_part1 + height_part2 + height_part3 + height_part5 + height_part6 + height_part75 + height_part7 +
              height_part85 + height_part8 + height_part95) && h <= (height_part0 + 25 + 6*skip_height + height_part1 + height_part2 + height_part3 + height_part5 + height_part6 + height_part75 + height_part7 +
              height_part85 + height_part8 + height_part95 + height_part9)){
            return 1
          } else if (h > (height_part0 + 25 + 6*skip_height + height_part1 + height_part2 + height_part3 + height_part5 + height_part6 + height_part75 + height_part7 +
              height_part85 + height_part8 + height_part95 + height_part9)){
            return 0
          }
        }        
      }
    },
    emit_time_filter(){
      console.log('in emit');
      this.$emit("time_filtered", this.cluster_stop, this.cluster_start);
    },
    filter_remove(){
       this.brush_time();
       this.$emit('time_filter_remove');
       document.getElementById('filter_time').style.opacity= '0%';
    },
    converter(val){
      let array = [];
      for(let i=0; i< val[2].length; i++){
        array.push(conversion.indexOf(val[2][i]));
      }
      return [val[0], val[1], array]
    }, 
    high_remove(){
      this.highlight = null;
      document.getElementById('high_time').style.opacity = '0%';
      document.getElementById('high_time_text').innerHTML = '';
    }
  },
  created() {
    console.log('timeline created');
    if(this.data_to_child[6]){
      this.highlight = this.converter(this.data_to_child[6]);  
    }    
    this.clustersNotes = this.data_to_child[1];
    this.clustersNotes.clusters = this.reverse(this.clustersNotes.clusters);
    this.notes = this.data_to_child[0];
    this.search_text = this.data_to_child[2];
    this.search = this.data_to_child[3];
    // to get the note button in the cluster boxes per cluster id
    // cluster.id ==0 is index 0 in clusterNoteButtons.
    // [[id note, date note], [id note, date note]] > per cluster
    for (let i = 0; i < this.clustersNotes.clusters.length; i++) {
      let cluster_name = this.clustersNotes.clusters[i].name;
      let tmp = this.notes.Notes.filter((note) => note.cluster == cluster_name);
      let results = [];
      for (let note of tmp) {
        results.push([note.id, note.date_start, note.text, note.title]);
      }
      this.clusterNoteButtons = [...this.clusterNoteButtons, results];
    }   
    //check if window gets resized
    window.addEventListener("resize", this.windows_size);
  },
  mounted() {
    console.log(this.highlight);
    if(this.highlight){
      console.log('in loop');
      document.getElementById('high_time').style.opacity = '100%';
      document.getElementById('high_time_text').innerHTML = 'Delete current highlight of co-occurence of ' + this.highlight[0] + 
        ' and ' +  this.highlight[1]; 
    }
    if (this.clustersNotes.clusters.length > 0) {
      this.makeTimeline();
    }
    if (this.data_to_child[4] == true) {
      this.noteOpen(this.data_to_child[5]);
    }
    
  },
  watch: {
    data_to_child() {
      this.search_text = this.data_to_child[2];
      this.search = this.data_to_child[3];
    },
    cluster_stop(){
      this.emit_time_filter();
    },
    cluster_start(){
      this.emit_time_filter();
    }
  },
};
</script>


<style>
.full_height {
  height: 100vh;
}
.height_90 {
  height: 70vh;
}
.dot {
  height: 25px;
  width: 25px;
  background-color: #bbb;
  border-radius: 50%;
  display: block;
}
.vl5 {
  border-left: 5px solid #bbb;
  height: 25vh;
  margin-left: 10px;
}
.vl2 {
  border-left: 2px solid #bbb;
  height: 25vh;
  margin-left: 10px;
}
.vl1 {
  border-left: 1px solid #bbb;
  height: 25vh;
  margin-left: 10px;
}
.vl-dashed5 {
  border-left: 5px dashed #bbb;
  height: 25vh;
  margin-left: 10px;
}
.margin_left_30 {
  margin-left: 30%;
}
.margin-top-line {
  margin-top: -8px;
}
.margin-bottom-line {
  margin-bottom: 8px;
}
.margin-side-small5 {
  margin-left: 5px !important;
}
.margin-side-small2 {
  margin-left: 2px !important;
}
.margin-side-small1 {
  margin-left: 1px !important;
}
.small_vertical_bar {
  width: 2px;
  height: 10px;
  background-color: #bbb;
  margin-top: -2.5px;
}
.bar_to_cluster_stripe {
  height: 5px;
  background-color: var(--dark-grey) !important;
}
</style>
