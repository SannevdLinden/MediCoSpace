<template>
  <div >
    <h2 class='header'><a id ='heatmap' @click="heatmap_all">
        Co-occurence diseases, drugs and treatments</a><span id ='zoom' style="font-size:12px;"></span></h2>
    Order: 
    <select id="order">
    <option value="name">Name</option>
    <option value="category">Category</option>
    <option value="freq_p">Frequency patient</option>
    <option value="freq_pop">Frequency population</option>
    </select>

    Population setting: 
    <select id="pop_setting">
    <option value="absolute">Absolute</option>
    <option value="relative">Relative</option>
    </select>

    <p id='filter_freq' v-show="filter_freq_text">
      Current frequency filter, min: {{min}} and max: {{max}}
      <button
      v-on:click="filter_remove"
      class="delete"
      style="margin-left:0.5rem"
    >
      
    </button>
    </p>
    
    <div style="display: flex">  
      <div id="legend" style="margin-top: 20px;"></div>    
      <div id="my_dataviz" style="margin: 10px;"></div>
      
    </div>
  </div>
</template>

<script>
import * as d3 from "d3";
import data_heatmap from './../assets/16961_aggregated.json'
import categories from './../assets/cat_16961_df.json'
import data_detail from './../assets/16961_aggregated_rows.json'

export default {
  name: 'Heatmap',
  props: ["time_filter"],
  data (){
    return{
      all_concepts: [],
      data_aggr_filter: [],
      data_detail_filter: {},
      filter: false, 
      current_cell: 'aggregated;aggregated', 
      min: 1,
      max: 0,
      filter_freq_text: false,
      concepts_scatter_filter: new Set(), 
      aggregated: false

    }
  },
  methods: {    
    heatmap(refresh, data_graph, aggregated, pop_setting){
        // https://www.d3-graph-gallery.com/graph/heatmap_style.html        
        this.aggregated = aggregated;
        this.$emit('aggregated_heatmap', aggregated);
        if(refresh){
          d3.select("#my_dataviz").selectAll('*').remove();
          d3.select("#legend").selectAll('*').remove();
        }  
             
        var margin = {top: 10, right: 0, bottom: 100, left: 100};
        var element = document.getElementById('scatterplots');        
        var height = element.offsetHeight * 0.78;
        var width = height;

        // append the svg object to the body of the page
        var svg = d3.select("#my_dataviz")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform",
                "translate(" + margin.left + "," + margin.top + ")");
        
        let data;
        console.log(this.filter);
        console.log(aggregated);
        console.log(this.current_cell);
        if(this.filter && aggregated){
          data = this.data_aggr_filter;
          this.current_cell = 'aggregated;aggregated';
        } else if (aggregated){
          data = data_graph;
          this.current_cell = 'aggregated;aggregated';
        } else {          
          if(this.filter){
            data = this.data_detail_filter[this.current_cell];
            data = this.remove_zero(data);
          } else {
            data = this.remove_zero(data_graph);
          }                    
        }       
        
        let max_val = 0;
        for(let i=0; i<data.length; i++){
          if (data[i].val > max_val){
            max_val = data[i].val;
          }
        }
        console.log(data);
        // Labels of row and columns -> unique identifier of the column called 'group' and 'variable'
        var myGroups = d3.map(data, function(d){return d.concepta;})
        myGroups = new Set(myGroups);
        myGroups = Array.from(myGroups);
        let labels_y_complete = myGroups;
        let count_label_y = 1;
        var myVars = d3.map(data, function(d){return d.conceptb;});
        myVars = new Set(myVars);
        myVars = Array.from(myVars);
        console.log(myVars);
        let labels_y = [];
        for(let i=0; i < myVars.length; i++){
          labels_y.push(count_label_y.toString() + '.' + myVars[i].substring(0,10));
          count_label_y ++;
        }
        console.log(labels_y);

        // color scale 
        // Log Scale
        let end = 0;
        if(aggregated){
          end = d3.map(data, function(d){if(d.group == 'diagonal') {return Math.max(...d.val)} return d.val;});          
        } else {
          end = d3.map(data, function(d){return d.val});
        }
        end = Math.max(...end);
        
        const logScale = d3.scaleLog()
          .domain([1, end+1])
        const colorScaleLog = d3.scaleSequential(
        (d) => d3.interpolateViridis(logScale(d))
      )   
      
        // Build X scales and axis:
        let max_label_x = false;
        let count_x = 0;
        if(myGroups.length > 50){
          max_label_x = true;
        }
        var x = d3.scaleBand()
            .range([ 0, width ])
            .domain(myGroups)
            .padding(0.05);
        
        svg.append("g") 
            .style("font-size", 10)
            .attr("transform", "translate(0," + height + ")") 
            .attr('class', 'colLabel')                 
            .call(d3.axisBottom(x).tickSize(0))
            .selectAll("text")  
            .style("text-anchor", "end")   
            .attr("transform", "rotate(-65)")  
            .attr('id', function(d){
              let string_text = d.toLowerCase();
              string_text = string_text.replace('diseases of the ','');
              string_text = string_text.replace('disease of ','');
              string_text = string_text.replace('certain ','');
              string_text = string_text.substring(0,15)
              string_text = string_text.replaceAll(',','');
              string_text = string_text.replaceAll(' ','');
              return "axis_labelx_" + string_text})
            .text(function(d){
              let string_text = d.toLowerCase();
              string_text = string_text.replace('diseases of the ','');
              string_text = string_text.replace('disease of ','');
              string_text = string_text.replace('certain ','');
              if(max_label_x){
                let number = Math.ceil(myGroups.length / 50);
                if (count_x % number == 0){
                  count_x ++;
                  return string_text.substring(0,15);
                } else {
                  count_x ++;
                  return '';
                }
              } else {
                return string_text.substring(0,15);
              }})
            .style('fill', function(d){
              let label, tmp; 
                if (aggregated){
                  tmp = Object.keys(categories['category']).find(key => categories['category'][key] === d);
                  label = categories['label'][tmp];
                } else {
                  tmp = Object.keys(categories['concept']).find(key => categories['concept'][key] === d);
                  label = categories['label'][tmp];
                }                
                if(label == 'procedure'){
                  return '#d95f02'
                  } else if (label == 'disease') {
                    return '#7570b3';
                  } else {
                    return '#1b9e77'
                  }}) 
            .on("click", function(d) {
              method.$emit('axis_labels', d['path'][0].innerHTML);
              let str = d['path'][0].innerHTML.replaceAll(' ', '');
              str = str.replaceAll(',','');
              d3.select('#axis_labelx_' + str)
              .style('text-decoration', 'underline');
              });       
         
        d3.select('.colLabel').selectAll('.tick')
          .attr('class', 'tick colLabelTick'); 

        // Build Y scales and axis:
        let max_label_y = false;
        let count_y = 0;
        if(myVars.length > 50){
          max_label_y = true;
        }
        var y = d3.scaleBand()
            .range([ height, 0 ])
            .domain(myVars)
            .padding(0.05);
        svg.append("g")
            .style("font-size", 10)
            .attr('class', 'rowLabel')
            .call(d3.axisLeft(y).tickSize(0))
            .selectAll("text")  
            .style("text-anchor", "end") 
            .attr('id', function(d){
              let string_text = d.toLowerCase();
              string_text = string_text.replace('diseases of the ','');
              string_text = string_text.replace('disease of ','');
              string_text = string_text.replace('certain ','');
              string_text = string_text.substring(0,15)
              string_text = string_text.replaceAll(',','');
              string_text = string_text.replaceAll(' ','');
              return "axis_labely_" + string_text})      
            .text(function(d){
              let string_text = d.toLowerCase();
              string_text = string_text.replace('diseases of the ','');
              string_text = string_text.replace('disease of ','');
              string_text = string_text.replace('certain ','');
              if(max_label_y){
                let number = Math.ceil(myVars.length / 50);
                if (count_y % number == 0){
                  count_y ++;
                  return string_text.substring(0,15);
                } else {
                  count_y ++;
                  return '';
                }
              } else {
                return string_text.substring(0,15);
              }})
            .style('fill', function(d){
                let label, tmp; 
                if (aggregated){
                  tmp = Object.keys(categories['category']).find(key => categories['category'][key] === d);
                  label = categories['label'][tmp];
                } else {
                  tmp = Object.keys(categories['concept']).find(key => categories['concept'][key] === d);
                  label = categories['label'][tmp];
                }   
                if(label == 'procedure'){
                  return '#d95f02'
                  } else if (label == 'disease') {
                    return '#7570b3';
                  } else {
                    return '#1b9e77'
                  }})  
            .on("click", function(d) {
              method.$emit('axis_labels', d['path'][0].innerHTML);
              let str = d['path'][0].innerHTML.replaceAll(' ', '');
              str = str.replaceAll(',','');
              d3.select('#axis_labely_' + str)
              .style('text-decoration', 'underline');
              });   
        
        d3.select('.rowLabel').selectAll('.tick')
          .attr('class', 'tick rowLabelTick');

        // color lines axis
        document.getElementsByClassName("domain")[0].style.color = '#F2F2F2'
        document.getElementsByClassName("domain")[1].style.color = '#F2F2F2'
        
               
        // create a tooltip
        var tooltip = d3.select("#my_dataviz")
            .append("div")
            .style("position", "absolute")
            .style("z-index", "4")
            .style("display", 'none')
            .attr("class", "tooltip")
            .style("background-color", "white")
            .style("border", "solid")
            .style("border-width", "2px")
            .style("border-radius", "5px")
            .style("padding", "5px")
        
        
        let current_cell = this.current_cell;
        let method = this;
        // Three function that change the tooltip when user hover / move / leave a cell
        const mouseover = function(event,d) {                
            let opposite_val = 'not displayed in this matrix';
            if(current_cell.split(';')[0] == current_cell.split(';')[1]){
               let opposite_rect = svg.select("rect[id='"+d.conceptb+':'+d.concepta + "']"); 
              if(opposite_rect.data()[0]){
                opposite_val = opposite_rect.data()[0]['val'];
              }
              opposite_rect
              .style('stroke', 'black')
              .attr('stroke-width', '4');    
            }                    
            tooltip
            .style("display", 'block')
            d3.select(this)
            .style('stroke', 'black')
            .attr('stroke-width', '4'); 
            console.log(event);
                        
            if(d.group == 'population'){
              tooltip
                .html("The population's co-occurrence of  <br>" + d.concepta + " and <br>" + d.conceptb +
                  "<br> is: " + d.val + "<br> The patient's occurence is: " + opposite_val)
                .style("left", event.x  + "px")
                .style("top", (event.y - 150) + "px")
            } else if (d.group == 'patient'){
              tooltip
                .html("The patient's co-occurrence of  <br>" + d.concepta + " and <br>" + d.conceptb +
                  "<br> is: " + d.val + "<br> The populations's occurence is: " + opposite_val)
                .style("left", event.x  + "px")
                .style("top", (event.y - 150) + "px")
            } else {
              if(aggregated){
                tooltip
                .html("The co-occurrence of  <br>" + d.concepta + " and <br>" + d.conceptb +
                  "<br> for the patient is: " + d.val[0] + " and for the populations is: " + d.val[1])
                .style("left", event.x  + "px")
                .style("top", (event.y - 150) + "px")
              } else {
                tooltip
                .html("The co-occurrence of  <br>" + d.concepta + " and <br>" + d.conceptb +
                  " is zero")
                .style("left", event.x  + "px")
                .style("top", (event.y - 150) + "px")
              }
              
            }
            if(document.getElementsByClassName('cell selected').length == 0){
              if(aggregated){
                let concepts_scatter_high = new Set();
                for(let i =0; i< data_detail[d.concepta + ';' + d.conceptb].length; i++){
                  concepts_scatter_high.add(data_detail[d.concepta + ';' + d.conceptb][i]['concepta']);
                  concepts_scatter_high.add(data_detail[d.concepta + ';' + d.conceptb][i]['conceptb']);
                }
                concepts_scatter_high = Array.from(concepts_scatter_high);
                method.$emit('highlight_scatter', concepts_scatter_high);
              } else {
                method.$emit('highlight_scatter', [d.concepta, d.conceptb]);
              } 
            }
        }        
        const mouseleave = function(event,d) {
          if(current_cell.split(';')[0] == current_cell.split(';')[1]){
            let opposite_rect = svg.select("rect[id='"+d.conceptb+':'+d.concepta + "']");
            opposite_rect
            .style('stroke', '#CECDCD')
            .attr('stroke-width', '1');  
          }            
            tooltip
            .style("display", 'none')
            d3.select(this)
            .style('stroke', '#CECDCD')
            .attr('stroke-width', '1');
            console.log(event);
            if(document.getElementsByClassName('cell selected').length == 0){
              method.$emit('highlight_scatter', 'no_high');
            }
        }
        let count = 0;
        let count_str = '';
        let color_p = '';
        let color_pop = '';
        // on click zoom in to cell
        // add the squares
        svg.selectAll()
            .data(data, function(d) {return d.concepta+':'+d.conceptb;})
            .enter()
            .append("rect")
            .attr("x", function(d) { return x(d.concepta) })
            .attr("y", function(d) { return y(d.conceptb) })
            .attr("rx", 4)
            .attr("ry", 4)
            .attr("id", function(d){ return d.concepta+':'+d.conceptb})            
            .attr("width", x.bandwidth() )
            .attr("height", y.bandwidth() )
            .style('stroke', '#CECDCD')
            .attr('stroke-width', '1')
            .attr('class', 'cell')
            .style("fill", function(d) {if(d.val == 0){return 'white'} else if (d.group == 'diagonal') 
                {//gradient                   
                  count_str = count.toString();
                  color_p = colorScaleLog(d.val[0]+1);
                  color_pop = colorScaleLog(d.val[1]+1);
                  if (d.val[0] == 0){
                    color_p = 'white';
                  }
                  if (d.val[1] == 0){
                    color_pop = 'white';
                  }
                  var gradient = svg.append("defs")
                      .append("linearGradient")
                        .attr("id", "gradient" + count_str)
                        .attr("x1", "0%")
                        .attr("y1", "50%")
                        .attr("x2", "50%")
                        .attr("y2", "100%")
                        .attr("spreadMethod", "pad");

                      gradient.append("stop")
                          .attr("offset", "50%")
                          .attr("stop-color", color_pop)
                          ;

                      gradient.append("stop")
                          .attr("offset", "50%")
                          .attr("stop-color", color_p)
                          ;

                  count ++;
                  return "url(#gradient" +  count_str + ")"
                  } else{ return colorScaleLog(d.val+1) }} )
            
            .on("mouseover", mouseover)
            .on("mouseleave", mouseleave)
            .on("click", function(event, d) {method.heatmap_zoom(event, d);});

           //color legend
           method.continuous("#legend", end, aggregated);
        
              
        //reordering axis
        d3.select("#order").on("change",function(){
          order(this.value);
        });
        var select = document.getElementById('order');
        var value = select.options[select.selectedIndex].value;
        if(value != 'name'){
          order(value);
        }        

        function order(value){  
          var t; 
          let cell_w = x.bandwidth() + (x.bandwidth()/18);
          let cell_h = y.bandwidth() + (y.bandwidth()/18);    
          if(value == 'name'){ 
            t = svg.transition().duration(1500);           
            t.selectAll("rect")
              .attr("x", function(d) { return x(d.concepta); })
              .attr("y", function(d) { return y(d.conceptb); })
              ;

            t.selectAll(".rowLabelTick")
              .attr("transform", function (d) { return 'translate(0,' + (y(d) + cell_h/2) + ')'; })
              ;

            t.selectAll(".colLabelTick")
              .attr("transform", function (d) {return 'translate(' + (x(d) + cell_w/2) + ',0)'; })
              ;
          } else if (value == 'category' && aggregated){
            t = svg.transition().duration(1500);
            let disease_list = new Set();            
            let drug_list = new Set();
            let procedure_list = new Set();
            for(let i=0; i < Object.keys(categories['category']).length; i++){
              if(categories['label'][i] == 'drug' && labels_y_complete.includes(categories['category'][i])){
                drug_list.add(categories['category'][i]);
              } else if (categories['label'][i] == 'disease' && labels_y_complete.includes(categories['category'][i])){
                disease_list.add(categories['category'][i]);
              } else {
                if(labels_y_complete.includes(categories['category'][i])){
                  procedure_list.add(categories['category'][i]);
                }
              }              
            }
            disease_list = Array.from(disease_list);
            drug_list = Array.from(drug_list);
            procedure_list = Array.from(procedure_list);

          t.selectAll("rect")
            .attr("x", function(d) { 
              let tmp = Object.keys(categories['category']).find(key => categories['category'][key] === d.concepta);
              let label = categories['label'][tmp];
              if(label == 'procedure'){
                return (cell_w * procedure_list.indexOf(d.concepta)) + ((disease_list.length + 
                    drug_list.length) * cell_w);
              } else if (label == 'disease') {
                return cell_w * disease_list.indexOf(d.concepta);
              } else {
                return (cell_w * drug_list.indexOf(d.concepta)) + (disease_list.length * cell_w);
              }})
            .attr("y", function(d) {
              let tmp = Object.keys(categories['category']).find(key => categories['category'][key] === d.conceptb);
              let label = categories['label'][tmp];
              if(label == 'procedure'){
                return cell_h * (procedure_list.length - procedure_list.indexOf(d.conceptb) -1);
              } else if (label == 'disease') {
                return cell_h * (disease_list.length - disease_list.indexOf(d.conceptb) -1) + ((procedure_list.length + 
                  drug_list.length) * cell_h);
              } else {
                return (cell_h * (drug_list.length - drug_list.indexOf(d.conceptb) -1)) + (procedure_list.length * cell_h);
              }})
            ;

            t.selectAll(".colLabelTick")
              .attr("transform", function (d) {
                let tmp = Object.keys(categories['category']).find(key => categories['category'][key] === d);
                let label = categories['label'][tmp];
                let x_trans;
                if(label == 'procedure'){
                  x_trans = (cell_w * procedure_list.indexOf(d)) + ((disease_list.length + 
                    drug_list.length) * cell_w) + cell_w/2;
                  return 'translate(' + x_trans + ', 0)';
                  } else if (label == 'disease') {
                    x_trans = cell_w * disease_list.indexOf(d) + cell_w/2;
                    return 'translate(' + x_trans + ', 0)';
                  } else {
                    x_trans = (cell_w * drug_list.indexOf(d)) + (disease_list.length * cell_w) + cell_w/2;
                    return 'translate(' + x_trans + ', 0)';
                  }});
            
            t.selectAll(".rowLabelTick")
              .attr("transform", function (d) {
                let tmp = Object.keys(categories['category']).find(key => categories['category'][key] === d);
                let label = categories['label'][tmp];
                let y_trans;
                if(label == 'procedure'){
                  y_trans = cell_h * (procedure_list.length - procedure_list.indexOf(d) -1) + cell_h/2;
                  return 'translate(0,' + y_trans + ')';
                } else if (label == 'disease') {
                  y_trans = cell_h * (disease_list.length - disease_list.indexOf(d) -1) + ((procedure_list.length + 
                  drug_list.length) * cell_h)+ cell_h/2;                    
                  return 'translate(0,' + y_trans + ')';
                } else {
                  y_trans = (cell_h * (drug_list.length - drug_list.indexOf(d) -1)) + (procedure_list.length * cell_h) + cell_h/2;
                  return 'translate(0,' + y_trans + ')';
                }});
          } else if (value == 'freq_p' || value == 'freq_pop'){
            let freqs = [];
            let concepta = '';
            let freqs_concept = [];
            for(let i=0; i< data.length; i++){
              if(data[i]['concepta'] != concepta){
                if(i > 0 && freqs_concept.length > 0){
                  let sum = 0;
                  for (let j = 0; j < freqs_concept.length; j++) {
                      sum += freqs_concept[j];
                  }
                  sum = Math.ceil(sum/freqs_concept.length);
                  freqs.push([concepta, sum])
                }
                concepta = data[i]['concepta'];
                freqs_concept = [];
              }
              if(data[i]['group'] == 'patient' && value == 'freq_p'){
                freqs_concept.push(data[i]['val']);
              } else if (data[i]['group'] == 'diagonal'){
                if(value == 'freq_p'){
                  freqs_concept.push(data[i]['val'][0]);
                } else {
                  freqs_concept.push(data[i]['val'][1]);
                }                
              } else if (data[i]['group'] == 'population' && value == 'freq_pop'){
                freqs_concept.push(data[i]['val']);
              }
              if(i == data.length -1){
                if(i > 0 && freqs_concept.length > 0){
                  let sum = 0;
                  for (let j = 0; j < freqs_concept.length; j++) {
                      sum += freqs_concept[j];
                  }
                  sum = Math.ceil(sum/freqs_concept.length);
                  freqs.push([concepta, sum])
                }
              }
            }
            freqs.sort(compareSecondColumn);
            console.log(freqs);

            if(value == 'freq_p'){
              t = svg.transition().duration(1500);
              t.selectAll("rect")
                .attr("x", function(d) { 
                let x_trans = freqs.findIndex(mulitDimIndex(d.concepta)) * cell_w;
                return x_trans; 
              })
              .attr("y", function(d) { 
                let y_trans = (freqs.length - 1 - freqs.findIndex(mulitDimIndex(d.conceptb))) * cell_h;
                return y_trans; });
              
              t.selectAll(".colLabelTick")
                .attr("transform", function (d) {
                  let x_trans = freqs.findIndex(mulitDimIndex(d)) * cell_w + cell_w/2;
                  return 'translate(' + x_trans + ', 0)';
                });
              
              t.selectAll(".rowLabelTick")
                .attr("transform", function (d) { 
                  let y_trans = (freqs.length - 1 - freqs.findIndex(mulitDimIndex(d))) * cell_h + cell_h/2;
                  return 'translate(0,' + y_trans + ')'; })
                ; 
            } else {
              t = svg.transition().duration(1500);
              t.selectAll("rect")
                .attr("y", function(d) { 
                let y_trans = (freqs.length - 1 - freqs.findIndex(mulitDimIndex(d.conceptb))) * cell_h;
                return y_trans; 
              })
              .attr("x", function(d) { 
                let x_trans = freqs.findIndex(mulitDimIndex(d.concepta)) * cell_w;
                return x_trans});
              
              t.selectAll(".rowLabelTick")
                .attr("transform", function (d) {
                  let y_trans = (freqs.length - 1 - freqs.findIndex(mulitDimIndex(d))) * cell_h + cell_h/2;
                  return 'translate(0,' + y_trans + ')';
                });
              
              t.selectAll(".colLabelTick")
                .attr("transform", function (d) {
                  let x_trans =  freqs.findIndex(mulitDimIndex(d)) * cell_w + cell_w/2;
                  return 'translate(' + x_trans + ',0)'; })
                ;
            }
            
          }
        }

        function compareSecondColumn(a, b) {
          if (a[1] === b[1]) {
              return 0;
          }
          else {
              return (a[1] < b[1]) ? -1 : 1;
          }
        }

        function mulitDimIndex(value) {
          return function(innerArr){
            return innerArr[0] === value;
          }
        }

        //population settings
        d3.select("#pop_setting").on("change",function(){
          pop_setting_change(this.value);
        });
        var select_pop = document.getElementById('pop_setting');
        var value_pop = select_pop.options[select_pop.selectedIndex].value;
        if(value_pop != 'absolute'){
          pop_setting_change(value_pop);
        }         
        function pop_setting_change(value){
          console.log(value);
          console.log(pop_setting);  
          let cells = svg.selectAll('rect')
          let min_rel = 0;
          let max_rel = 0;
          for(let i=0; i<data.length; i++){
            if(aggregated){
              if(data[i]['group'] == 'population' || data[i]['group'] == 'diagonal')
                if(data[i]['pop_rel'] < min_rel){
                  min_rel = data[i]['pop_rel'];
                } else if(data[i]['pop_rel'] > max_rel){
                  max_rel = data[i]['pop_rel'];
                }
            } else {
              if(data[i]['group'] == 'population')
                if(data[i]['pop_rel'] < min_rel){
                  min_rel = data[i]['pop_rel'];
                } else if(data[i]['pop_rel'] > max_rel){
                  max_rel = data[i]['pop_rel'];
                }
            }
          }

          let color_scale_rel = d3.scaleSequential()
            .interpolator(d3.interpolateRdBu)
            .domain([min_rel, max_rel]);

          const mouseover_rel = function(event,d) {                
            let opposite_val = 'not displayed in this matrix';
            let opposite_val_rel = 'not displayed in this matrix';
            if(current_cell.split(';')[0] == current_cell.split(';')[1]){
               let opposite_rect = svg.select("rect[id='"+d.conceptb+':'+d.concepta + "']"); 
              if(opposite_rect.data()[0]){
                opposite_val = opposite_rect.data()[0]['val'];
                opposite_val_rel = opposite_rect.data()[0]['pop_rel'];
              }
              opposite_rect
              .style('stroke', 'black')
              .attr('stroke-width', '4');    
            }                    
            tooltip
            .style("display", 'block')
            d3.select(this)
            .style('stroke', 'black')
            .attr('stroke-width', '4'); 
            console.log(event);
                        
            if(d.group == 'population'){
              tooltip
                .html("The population's co-occurrence of  <br>" + d.concepta + " and <br>" + d.conceptb +
                  "<br> is " + d.pop_rel + " more or less than the patient's occurence of: <br>" + opposite_val)
                .style("left", event.x  + "px")
                .style("top", (event.y - 150) + "px")
            } else if (d.group == 'patient'){
              tooltip
                .html("The patient's co-occurrence of  <br>" + d.concepta + " and <br>" + d.conceptb +
                  "<br> is: " + d.val + "<br> The populations's difference is: " + opposite_val_rel)
                .style("left", event.x  + "px")
                .style("top", (event.y - 150) + "px")
            } else {
              if(aggregated){
                tooltip
                .html("The co-occurrence of  <br>" + d.concepta + " and <br>" + d.conceptb +
                  "<br> for the patient is: " + d.val[0] + " and the difference with the populations is: " + d.pop_rel)
                .style("left", event.x  + "px")
                .style("top", (event.y - 150) + "px")
              } else {
                tooltip
                .html("The co-occurrence of  <br>" + d.concepta + " and <br>" + d.conceptb +
                  " is zero")
                .style("left", event.x  + "px")
                .style("top", (event.y - 150) + "px")
              }
              
            }
            if(document.getElementsByClassName('cell selected').length == 0){
              if(aggregated){
                let concepts_scatter_high = new Set();
                for(let i =0; i< data_detail[d.concepta + ';' + d.conceptb].length; i++){
                  concepts_scatter_high.add(data_detail[d.concepta + ';' + d.conceptb][i]['concepta']);
                  concepts_scatter_high.add(data_detail[d.concepta + ';' + d.conceptb][i]['conceptb']);
                }
                concepts_scatter_high = Array.from(concepts_scatter_high);
                method.$emit('highlight_scatter', concepts_scatter_high);
              } else {
                method.$emit('highlight_scatter', [d.concepta, d.conceptb]);
              } 
            }
        }
          if(value == 'relative'){
            cells.on('mouseover', mouseover_rel);
          } else {
            cells.on('mouseover', mouseover);
          }
          
          cells.style("fill", function(d) {
            if(d.val == 0){return 'white'}
            else if(d.group == 'population' && value == 'relative'){
              return color_scale_rel(d.pop_rel)
            } else if (d.group == 'diagonal') 
                {//gradient                   
                  count_str = count.toString();
                  color_p = colorScaleLog(d.val[0]+1);
                  if(value == 'relative'){
                    color_pop = color_scale_rel(d.pop_rel);
                  } else {
                    color_pop = colorScaleLog(d.val[1]+1);
                  }                  
                  if (d.val[0] == 0){
                    color_p = 'white';
                  }
                  if (d.val[1] == 0){
                    color_pop = 'white';
                  }
                  var gradient = svg.append("defs")
                      .append("linearGradient")
                        .attr("id", "gradient" + count_str)
                        .attr("x1", "0%")
                        .attr("y1", "50%")
                        .attr("x2", "50%")
                        .attr("y2", "100%")
                        .attr("spreadMethod", "pad");

                      gradient.append("stop")
                          .attr("offset", "50%")
                          .attr("stop-color", color_pop)
                          ;

                      gradient.append("stop")
                          .attr("offset", "50%")
                          .attr("stop-color", color_p)
                          ;

                  count ++;
                  return "url(#gradient" +  count_str + ")"
                  } else{ return colorScaleLog(d.val+1) }} );
        }

    },
    heatmap_zoom(event, data){
      console.log("in zoom");
      console.log(event);
      console.log(data);
      let categorya = data['concepta'];
      let categoryb = data['conceptb'];
      if(this.aggregated){
        let index = categorya + ";" + categoryb;
        this.current_cell = index;
        let data_filtered = data_detail[index];    
        this.heatmap(true, data_filtered, false, false);
        document.getElementById('zoom').innerHTML = ' > ' + categorya + ", " + categoryb;
      } else {
        if(data.notes[0] != -1){
          this.$emit('notes-highlight', [categorya, categoryb, data.notes]);
        }        
      }    
    },
    // create continuous color legend
    continuous(name, end, aggregated) {
      var element = document.getElementById('scatterplots');
      let width = element.offsetHeight * 0.78;
      var domain = [1, end];
      var range = [0,width -10];
      var colour_range = [];
      for(let i=0; i <= 1; i += (1/9)){
        colour_range.push(d3.interpolateViridis(i))
      }
      colour_range.push(d3.interpolateViridis(1))
      let method = this;

      var svg = d3.select(name).append("svg")
        .attr("width", 75)
        .attr("height", width) 
        .append("g")
        .attr("transform", "translate(0, 3)"); 

      var logScale =  d3.scaleLog().domain(domain).range(range);
      //Map colours across the range in equal intervals
      var num_colours = colour_range.length;
      var diff = range[1] - range[0];

      var step = diff / (colour_range.length - 1);
      var for_inversion = d3.range(num_colours).map(function(d) {return range[0] + d*step});
      var log_colour_values = for_inversion.map(logScale.invert);     
      var logColour_scale = d3.scaleLog().domain(log_colour_values).range(colour_range);

      //Now plot rectangles
      var num_rectangles = 100     
      step = diff/num_rectangles
      var rect_data = d3.range(num_rectangles).map(function(d) {return range[0] + d*step})
     
      let tmp = svg.append('g');

      tmp.selectAll("rect").data(rect_data).enter()
        .append("rect")
        .attr("x", 0)
        .attr("y", function(d) {return d})
        .attr("height", diff/num_rectangles)
        .attr("width", 20)
      .attr("fill", function(d) {
        return logColour_scale(logScale.invert(d))
      })   
      
      var axis = d3.axisRight(logScale)
        .ticks(20, d3.format(","));    
      svg
        .append('g')
        .attr("transform", "translate(20, 0)")     
        .call(axis);
    
      tmp
      .call( d3.brushY() 
        .on('end', brushed)                      
        .extent( [ [0,0], [20,width] ] ) 
            
      )
           
      function brushed(){
        const sel = d3.brushSelection(this);        
        let y0 = logScale.invert(sel[0]);
        let y1 = logScale.invert(sel[1]);
        method.filter_data(Math.floor(y0), Math.ceil(y1), aggregated, [], 'freq');
      }

    },
    heatmap_all(){
      this.heatmap(true, data_heatmap, true, false);
      document.getElementById('zoom').innerHTML = '';
    },
    remove_zero(data){
      let columns_remove = this.remove('concepta', data); //remove 0 columns
      let row_remove = this.remove('conceptb', data); //remove 0 rows
      for(let i =0; i < columns_remove.length; i++){        
          data = data.filter(function(value){ 
              return value['concepta'] != columns_remove[i];
          });        
      }
      for(let i =0; i < row_remove.length; i++){        
          data = data.filter(function(value){ 
              return value['conceptb'] != row_remove[i];
          });        
      }
      return data;
    },
    remove(name, data){
      let vars = d3.map(data, function(d){return d[name];})
      vars = new Set(vars);
      vars = Array.from(vars);
      for(let i =0; i < data.length; i++){
        if(data[i]['val'] > 0){
          vars = vars.filter(function(value){ 
              return value != data[i][name];
          });
        }
      }
      return vars;
    },
    filter_data(min, max, aggregated, notes, type){  
      if(type == 'freq'){
        this.filter_freq_text = true;
      }  
      this.filter = true;      
      this.max = max;
      this.min = min;
      this.data_aggr_filter = [];
      this.data_detail_filter = {};  
      let keys = [];
      for(let i=0; i<data_heatmap.length; i++){
        keys.push(data_heatmap[i]['concepta'] + ";" + data_heatmap[i]['conceptb']);
        if(data_heatmap[i]['group'] != 'diagonal'){
          if(type == 'freq'){
            if(data_heatmap[i]['val'] >= min && data_heatmap[i]['val'] <= max){
                this.data_aggr_filter.push(data_heatmap[i]);
            } 
          }       
        } else {
          if(type == 'freq'){
            if((data_heatmap[i]['val'][0] >= min && data_heatmap[i]['val'][0] <= max) &&
              (data_heatmap[i]['val'][1] >= min && data_heatmap[i]['val'][1] <= max)){
              this.data_aggr_filter.push(data_heatmap[i]);
            }
          }
        }
        if(type == 'time'){          
          for(let j=0; j < notes.length; j++){
            if(data_heatmap[i]['notes'].includes(notes[j])){
              this.data_aggr_filter.push(data_heatmap[i]);  
              break;          
            }
          }           
        }        
      }
      for(let i =0; i < keys.length; i++){
        let tmp_array = [];
        for(let j=0; j< data_detail[keys[i]].length; j++){
          if(type == 'freq'){
            if(data_detail[keys[i]][j]['val'] <= max && data_detail[keys[i]][j]['val'] >= min){
              tmp_array.push(data_detail[keys[i]][j]);
              this.concepts_scatter_filter.add(data_detail[keys[i]][j]['concepta']);
              this.concepts_scatter_filter.add(data_detail[keys[i]][j]['conceptb']);
            }
          } else if (type == 'time'){
            for(let k=0; k < notes.length; k++){
              if(data_detail[keys[i]][j]['notes'].includes(notes[k])){
                tmp_array.push(data_detail[keys[i]][j]);
                this.concepts_scatter_filter.add(data_detail[keys[i]][j]['concepta']);
                this.concepts_scatter_filter.add(data_detail[keys[i]][j]['conceptb']); 
                break;          
              }
            }  
          }          
        }
        if(tmp_array.length > 0){
          this.data_detail_filter[keys[i]] = tmp_array;
        }
      }
      if(aggregated){
        this.heatmap(true, data_heatmap, aggregated, false);
      } else {
        if(this.data_detail_filter[this.current_cell]){
          this.heatmap(true,  this.data_detail_filter[this.current_cell], aggregated, false);
        } else {
          alert("The resulting heatmap will be empty")
        }        
      }
      this.$emit('concepts_scatter', this.concepts_scatter_filter);     
    },
    filter_remove(){
      this.filter = false;
      this.filter_freq_text = false;
      if(this.current_cell == 'aggregated;aggregated'){
        this.heatmap(true, data_heatmap, true, false);
      } else {
        this.heatmap(true, data_detail[this.current_cell], false, false);
      }
    }
    // heatmap_history(){       
    //     let data = [];
    //     let counter = 0;
    //     for(let i=0; i<data_heatmap.length; i++){                     
    //       counter += data_heatmap[i].notes.length;         
    //     }
    //     for(let i=0; i<counter; i++){ //number of concept combinations
    //       data.push({vala:'', valb:'', freq: 0})
    //     }
    //     let counter2 = 0;
    //     //all pairs of concept 1 and concept 2 per note
    //     for(let i=0; i<data_heatmap.length; i++){
    //       for(let j=0; j<data_heatmap[i].notes.length; j++){
    //         data[counter2].vala = data_heatmap[i].group;
    //         data[counter2].valb = data_heatmap[i].notes[j].toString() + '.' + data_heatmap[i].variable;
    //         data[counter2].freq = data_heatmap[i].values[j];
    //         counter2 ++;
    //       }
    //     }
    //     data.sort(function(a, b){return parseInt(a.valb.split('.')[0]) - parseInt(b.valb.split('.')[0])});
    //     let data_final = [];
    //     console.log(data);
    //     for(let i=0; i<data.length; i++){      
    //       for(let j=0; j<this.all_concepts.length; j++){
    //         if(data[i].vala == this.all_concepts[j]){
    //           data_final.push({group: data[i].vala, variable: data[i].valb, value: data[i].freq});
    //         } else{
    //           data_final.push({group: this.all_concepts[j], variable:data[i].valb, value: 0});
    //         }            
    //       }
    //     }
    //     this.heatmap(true, data_final, true); 
    // }
  },
  mounted() {
      this.heatmap(false, data_heatmap, true, false);
  },
  watch: {
    time_filter() {
      console.log(this.time_filter);
      if(this.time_filter == 'no_filter'){
        this.filter_remove();
      } else {
        this.filter_data(0, 0, this.current_cell == 'aggregated;aggregated', this.time_filter, 'time');
      }
      
    }
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
  color: var(--darkest-grey);
}


</style>
