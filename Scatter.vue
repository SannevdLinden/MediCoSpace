<template>
  <div >
    <h2 class='header'>Similarity diseases, drugs and treatments</h2>
    <p id='filter_freq' v-show="filter_brush">
      Remove brush filter
      <button
      v-on:click="filter_remove"
      class="delete"
      style="margin-left:0.5rem"
    /> 
    </p>   
    <h3 class="sub_header" style="color: #7570b3">Disease space</h3>
    <button
      v-on:click="zoom_to_brush('disease', true)"
      class="button button_style"
      id = 'button_zoom_disease'
      style="margin-top:0.2rem !important; margin-bottom:0.3rem !important;
        background-color: #474745 !important"
    >
      Zoom
    </button>
    <button
      v-on:click="zoom_to_brush('disease', false)"
      class="button button_style"
      id = 'button_brush_disease'
      style="margin:0.2rem 0 0.3rem 0.5rem !important;"
    >
     Brush
    </button>
    <div id="chart"></div>

    <h3 class="sub_header" style="color: #1b9e77">Drugs space</h3>
    <button
      v-on:click="zoom_to_brush('drug', true)"
      class="button button_style"
      id = 'button_zoom_drug'
      style="margin-top:0.2rem !important; margin-bottom:0.3rem !important;
        background-color: #474745 !important"
    >
      Zoom
    </button>
    <button
      v-on:click="zoom_to_brush('drug', false)"
      class="button button_style"
      id = 'button_brush_drug'
      style="margin:0.2rem 0 0.3rem 0.5rem !important;"
    >
     Brush
    </button>
    <div id="chart_drugs"></div>
    

    <h3 class="sub_header" style='color: #d95f02'>Treatment space</h3>
    <button
      v-on:click="zoom_to_brush('procedure', true)"
      class="button button_style"
      id = 'button_zoom_procedure'
      style="margin-top:0.2rem !important; margin-bottom:0.3rem !important;
        background-color: #474745 !important"
    >
      Zoom
    </button>
    <button
      v-on:click="zoom_to_brush('procedure', false)"
      class="button button_style"
      id = 'button_brush_procedure'
      style="margin:0.2rem 0 0.3rem 0.5rem !important;"
    >
     Brush
    </button>
    <div id="chart_treatments"></div>
  </div>
</template>

<script>
import * as d3 from "d3";
import disease_data from './../assets/disease.json'
import procedure_data from './../assets/procedure.json'
import drug_data from './../assets/drug.json'
import scatter_links from './../assets/scatter_occurence.json'

export default {
  name: 'Scatter',
  props: ["selection"],
  data (){
    return{
      zoom_disease: true,
      zoom_drug: true,
      zoom_procedure: true,
      svg_disease: null,
      svg_drug: null,
      svg_procedure: null,
    //   xAxis_disease: null,
    //   yAxis_disease : null,
      xScale_disease : null,
      yScale_disease : null,
      xScale_drug : null,
      yScale_drug : null,
      xScale_procedure : null,
      yScale_procedure : null,
    //   gX_disease : null,
    //   gY_disease : null,
      scatter_disease: null,
      scatter_drug: null,
      scatter_procedure: null,
      width: null,
      height: null, 
      scale_disease: {'x': 0, 'y': 0, 'k': 1},
      scale_drug: {'x': 0, 'y': 0, 'k': 1},
      scale_procedure: {'x': 0, 'y': 0, 'k': 1},
      disease_data: null,
      drug_data: null,
      procedure_data: null,
      max_occ: 0,
      filter_brush: false

    }
  },
    
  methods: {    
    scatter(data, svg, name, cat){
        //http://bl.ocks.org/feyderm/6bdbc74236c27a843db633981ad22c1b
        console.log(data);
        // set the dimensions and margins of the graph
        var element = document.getElementById('scatterplots');
        var width = element.offsetWidth * 0.9;
        var height = element.offsetHeight * 0.2;
        var margin = {top: 0, right:  0, bottom: 0, left: 0};

        d3.select("#" + cat + 'plot').remove();
        // append the svg object to the body of the page
        svg = d3.select(name)
            .append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
            .attr("style", "outline: solid #CECDCD;")
            .style("border-radius", "5px")
            .attr('id', cat + 'plot')
            .attr("viewBox", [0, 0, width, height]);
            
            // .append("g")
            //     .attr("transform",
            //         "translate(" + margin.left + "," + margin.top + ")");
        
        let x_domain = [0, 0]
        let y_domain = [0,0]
        if(name == '#chart'){
            x_domain[0] = disease_data['x']['min'];
            x_domain[1] = disease_data['x']['max'];
            y_domain[0] = disease_data['y']['min'];
            y_domain[1] = disease_data['y']['max'];
        } else if (name == '#chart_drugs'){
            x_domain[0] = drug_data['x']['min'];
            x_domain[1] = drug_data['x']['max'];
            y_domain[0] = drug_data['y']['min'];
            y_domain[1] = drug_data['y']['max'];
        } else {
            x_domain[0] = procedure_data['x']['min'];
            x_domain[1] = procedure_data['x']['max'];
            y_domain[0] = procedure_data['y']['min'];
            y_domain[1] = procedure_data['y']['max'];
        }
        
        // Add X axis
        var xScale  = d3.scaleLinear()
            .domain([x_domain[0], x_domain[1]])
            .range([ 0, width ]);
        // let xAxis = d3.axisBottom(xScale);
        // let gX= svg.append("g")
        //     .attr("transform", "translate(0," + height + ")")
        //     .call(xAxis);
        // console.log(gX);

        // Add Y axis
        var yScale = d3.scaleLinear()
            .domain([y_domain[0], y_domain[1]])
            .range([ height, 0]);
        // let yAxis = d3.axisLeft(yScale);
        // let gY= svg.append("g")
        //     .call(yAxis);
        // console.log(gY);

        //color scale 
        const logScale = d3.scaleLog()
          .domain([1, this.max_occ+1])
        let myColor;
        if(cat == 'disease'){
            myColor = d3.scaleSequential(
                (d) => d3.interpolatePurples(logScale(d)))   
        } else if(cat == 'drug'){
            myColor = d3.scaleSequential(
                (d) => d3.interpolateGreens(logScale(d)))   
        } else {
            myColor = d3.scaleSequential(
                (d) => d3.interpolateOranges(logScale(d)))   
        }        

        // create a tooltip
        var tooltip = d3.select(name)
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
        
        // Three function that change the tooltip when user hover / move / leave a cell
        const mouseover = function(event,d) { 
            tooltip
            .style("display", 'block')
            d3.select(this)
            .style("stroke", "black")
            .attr('stroke-width', '4')
            .style("opacity", 1)
            tooltip
            .html("This is concept: " + d.concept + '<br> with occurence in patient: ' + d.occ_p    
                + ' and average occurrence in population: ' + d.occ_pop)
            .style("left", event.x  + "px")
            .style("top", (event.y) + "px");   
        }        
        const mouseleave = function(event,d) {         
            tooltip
            .style("display", 'none')
            d3.select(this)
            .style('stroke', 'none')
            .style("opacity", 0.8)
            .style('stroke', '#CECDCD')
            .attr('stroke-width', '1');
            console.log(event);
            console.log(d);
        }

        // Add a clipPath: everything out of this area won't be drawn.
        // svg.append("defs").append("svg:clipPath")
        //     .attr("id", "clip")
        //     .append("svg:rect")
        //     .attr("width", width )
        //     .attr("height", height )
        //     .attr("x", 0)
        //     .attr("y", 0);

        // Create the scatter variable: where both the circles and the brush take place
        var scatter = svg.append('g')
            .attr("clip-path", "url(#clip)")  
            .attr('id', 'zoom_space' + cat)
            
        scatter
            .append("rect")
            // .attr('id', name + '_zoom')
            .attr("width", width)
            .attr("height", height)
            .style("fill", "#F2F2F2")
            .style("pointer-events", "all")

        // Add dots
        scatter
            .selectAll("dot")
            .data(data)
            .enter()            
            .append("circle")
            .attr("cx", function (d) {return xScale(d.x); } )
            .attr("cy", function (d) {return yScale(d.y); } )
            .attr("r", function(d){if(d.occ_p == 0){return 2} 
                else {return 5}})
            .attr('fill', function(d){if(d.occ_p == 0){return myColor(d.occ_pop)} 
                else {return myColor(d.occ_p)}})
            .attr('opacity', function(d){if(d.occ_p == 0){return 0.5} 
                else {return 1}})
            .attr('id', function(d){return d.concept})
            // .attr('opacity', function(d){if()})
            .on("mouseover", mouseover)
            .on("mouseleave", mouseleave)
            .attr("class", "non_brushed");
    
        this.width = width;
        this.height = height;
        if(name == '#chart'){
            this.svg_disease = svg;            
            // this.xAxis_disease = xAxis;
            // this.yAxis_disease = xAxis;
            this.xScale_disease = xScale;
            this.yScale_disease = yScale;
            // this.gX_disease = gX;
            // this.gY_disease = gY;
            this.scatter_disease = scatter;
            this.zoom_or_brush('disease');
        } else if (name == '#chart_drugs'){
            this.svg_drug = svg;
            this.xScale_drug = xScale;
            this.yScale_drug = yScale;
            this.scatter_drug = scatter;
            this.zoom_or_brush('drug');
        } else {
            this.svg_procedure = svg;
            this.xScale_procedure = xScale;
            this.yScale_procedure = yScale;
            this.scatter_procedure = scatter;
            this.zoom_or_brush('procedure');
        }
        
    },
    data_processing(data, cat){
        let final_data = [];
        let occ_pop, occ_p, links, notes;
        for (const [key, value] of Object.entries(data)) {
            for (let i =0; i < scatter_links.length; i++){
                if(scatter_links[i]['concept'] == key){
                    occ_pop = scatter_links[i]['occurence_pop'];
                    occ_p = scatter_links[i]['occurence_p'];
                    links = scatter_links[i]['links'];
                    notes = scatter_links[i]['note_links'];
                }
            }
            if(occ_pop > this.max_occ){
                this.max_occ = occ_pop;
            } else if (occ_p > this.max_occ){
                this.max_occ = occ_p;
            }
            if(this.selection != 'no_filter'){
                if(this.selection.includes(key)){
                    final_data.push({'concept': key, 'x': value[0], 'y': value[1], 
                    'occ_pop': occ_pop, 'occ_p': occ_p, 'notes': notes, 'links': links});
                }
            } else {
                final_data.push({'concept': key, 'x': value[0], 'y': value[1], 
                    'occ_pop': occ_pop, 'occ_p': occ_p, 'notes': notes, 'links': links});
            }           
        }
        if(cat == 'disease'){
            this.disease_data = final_data;
        } else if (cat == 'drug'){
            this.drug_data = final_data;
        } else {
            this.procedure_data = final_data;
        }
        return final_data;
    }, 
    zoom_to_brush(cat, zoom){        
        if(zoom){
            if(cat == 'disease'){
                this.zoom_disease = true;
                document.getElementById('button_zoom_disease').style.setProperty('background-color', '#474745', 'important');
                document.getElementById('button_brush_disease').style.setProperty('background-color', '#808080', 'important');
                this.zoom_or_brush('disease');                
            } else if(cat == 'drug'){
                this.zoom_drug = true;
                document.getElementById('button_zoom_drug').style.setProperty('background-color', '#474745', 'important');
                document.getElementById('button_brush_drug').style.setProperty('background-color', '#808080', 'important');
                this.zoom_or_brush('drug');                
            } else {
                this.zoom_procedure = true;
                document.getElementById('button_zoom_procedure').style.setProperty('background-color', '#474745', 'important');
                document.getElementById('button_brush_procedure').style.setProperty('background-color', '#808080', 'important');
                this.zoom_or_brush('procedure');                
            }
        } else{
            if(this.svg_disease.select('.selection')){
                this.svg_disease.select('.selection').remove();
                this.svg_disease.select('#brush_rect').remove();
            }  
            if(this.svg_drug.select('.selection')){
                this.svg_drug.select('.selection').remove();
                this.svg_drug.select('#brush_rect').remove();
            }  
            if(this.svg_procedure.select('.selection')){
                this.svg_procedure.select('.selection').remove();
                this.svg_procedure.select('#brush_rect').remove();
            }
            if(cat == 'disease'){
                this.zoom_disease = false;
                 document.getElementById('button_zoom_disease').style.setProperty('background-color', '#808080', 'important');
                document.getElementById('button_brush_disease').style.setProperty('background-color', '#474745', 'important');
                this.zoom_or_brush('disease');
            } else if(cat == 'drug'){
                this.zoom_drug = false;
                 document.getElementById('button_zoom_drug').style.setProperty('background-color', '#808080', 'important');
                document.getElementById('button_brush_drug').style.setProperty('background-color', '#474745', 'important');
                this.zoom_or_brush('drug');
            }else {
                this.zoom_procedure = false;
                 document.getElementById('button_zoom_procedure').style.setProperty('background-color', '#808080', 'important');
                document.getElementById('button_brush_procedure').style.setProperty('background-color', '#474745', 'important');
                this.zoom_or_brush('procedure');
            }
        }
        
    },
    zoom_or_brush(name){
        let width = this.width;
        let height = this.height;
        // let xAxis = this.xAxis_disease;
        // let yAxis = this.xAxis_disease;
        let svg, xScale, yScale, scatter, zoom_bool, scale;
        if(name == 'disease'){
            svg = this.svg_disease;
            xScale = this.xScale_disease;
            yScale = this.yScale_disease;
            scatter = this.scatter_disease;
            zoom_bool = this.zoom_disease;
            scale = this.scale_disease;
        } else if (name == 'drug'){
            svg = this.svg_drug;
            xScale = this.xScale_drug;
            yScale = this.yScale_drug;
            scatter = this.scatter_drug;
            zoom_bool = this.zoom_drug;
            scale = this.scale_drug;
        } else {
            svg = this.svg_procedure;
            xScale = this.xScale_procedure;
            yScale = this.yScale_procedure;
            scatter = this.scatter_procedure;
            zoom_bool = this.zoom_procedure;
            scale = this.scale_procedure;
        }
        
        // let gX = this.gX_disease;
        // let gY = this.gY_disease;
        
        var zoom;
        let method = this;

        if (zoom_bool){
            svg.select('.selection').remove();
            svg.select('#brush_rect').remove();
            // Pan and zoom
            zoom = d3.zoom()
                .scaleExtent([0.8, 20])
                .extent([[0, 0], [width, height]])
                .on("zoom", zoomed);
            
            d3.select('#zoom_space' + name)
                .call(zoom).call(zoom.transform, d3.zoomIdentity
                    .translate(scale.x, scale.y).scale(scale.k));
             
           
        } else {
            svg.on("zoom", null);           
            var brush = d3.brush()
                    .on("end", highlightBrushedCircles);

            svg
                .append("g")
                .attr('id', 'brush_rect')
                .call(brush); 
        }
         function zoomed({transform}) {
            method.get_scale(d3.zoomTransform(this), name);
            // create new scale ojects based on event
                var new_xScale = transform.rescaleX(xScale);
                var new_yScale = transform.rescaleY(yScale);
            // update axes
                // gX.call(xAxis.scale(new_xScale));
                // gY.call(yAxis.scale(new_yScale));
                scatter
                .selectAll("circle")
                .attr('cx', function(d) {return new_xScale(d.x)})
                .attr('cy', function(d) {return new_yScale(d.y)});
            }
         function highlightBrushedCircles() {  
                let selection, selection_connected;  
                let list = []; 
                let sel_concepts = [];      
                // revert circles to initial style
                d3.selectAll("circle").attr("class", "non_brushed");
                var brush_coords = d3.brushSelection(this);
                if(brush_coords){
                    // style brushed circles
                    selection = scatter.selectAll("circle").filter(function (){
                        var cx = d3.select(this).attr("cx"),
                            cy = d3.select(this).attr("cy"); 
                        return isBrushed(brush_coords, cx, cy);
                    });
                    // get all linked circles and color them
                    for(let i=0; i<selection.data().length; i++){
                        let tmp = selection.data()[i];
                        sel_concepts.push(selection.data()[i]['concept']);
                        if(tmp.occ_p > 0){
                            list = list.concat(selection.data()[i]['links']);
                        }  
                    }
                    list = new Set(list);
                    list = Array.from(list);
                    selection_connected = d3.selectAll("circle").filter(function (){
                        var name = d3.select(this).attr("id"); 
                        return list.includes(name);
                    })
                    .attr("class", "brushed_connected");
                    console.log(selection_connected);
                    selection.attr("class", "brushed");   
                    method.filter_brush = true;                 
                    method.$emit('scatter_brush_concepts', sel_concepts.concat(list));
                }           
            }
            
            function isBrushed(brush_coords, cx, cy) {
                var x0 = brush_coords[0][0],
                    x1 = brush_coords[1][0],
                    y0 = brush_coords[0][1],
                    y1 = brush_coords[1][1];
                return x0 <= cx && cx <= x1 && y0 <= cy && cy <= y1;
            }
    },
    get_scale(num, name){
        if(name == 'disease'){
            this.scale_disease = num;
        } else if (name == 'drug'){
            this.scale_drug = num;
        } else {
            this.scale_procedure = num;
        }        
    },
    filter_remove(){
        d3.select('.selection').remove();
        d3.select('#brush_rect').remove();
        d3.selectAll("circle").attr("class", "non_brushed");
        this.filter_brush = false;
        this.$emit('scatter_brush_concepts', 'no_selection');
        
    }
  },
  mounted() {
      var svg, svg_drugs, svg_treatments; 
      this.scatter(this.data_processing(disease_data['embeddings'], 'disease'), svg, "#chart", 'disease');
      this.scatter(this.data_processing(drug_data['embeddings'], 'drug'), svg_drugs, "#chart_drugs", 'drug');
      this.scatter(this.data_processing(procedure_data['embeddings'], 'procedure'), svg_treatments, "#chart_treatments", 'procedure');
  },
  watch: {
    selection() {
        console.log(this.selection);
        var svg, svg_drugs, svg_treatments; 
        this.scatter(this.data_processing(disease_data['embeddings'], 'disease'), svg, "#chart", 'disease');
        this.scatter(this.data_processing(drug_data['embeddings'], 'drug'), svg_drugs, "#chart_drugs", 'drug');
        this.scatter(this.data_processing(procedure_data['embeddings'], 'procedure'), svg_treatments, "#chart_treatments", 'procedure'); 
    
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style>
.brushed {
    stroke: #e7298a;
    stroke-width: 3;
}

.brushed_connected {
    stroke: black;
    stroke-width: 3;
}

.non_brushed {
    stroke-width: 1;
    stroke: #CECDCD;    
}
</style>
