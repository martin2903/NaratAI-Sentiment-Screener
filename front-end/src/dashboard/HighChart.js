import { useContext, useState,useEffect } from "react"
import Highcharts from 'highcharts';
import HighchartsReact from "highcharts-react-official";
import AppContext from "../App/app-state";

//The Highcharts component 
const HighChart =(props)=>{
  const appContext = useContext(AppContext)

  //The chart options are placed in a useState hook so that their values can be set and changed.
    const [options,setOptions]=useState({
      
        title: {
            text: 'Sentiment Score'
          },
          
          yAxis: {
            title: {
              text: 'Sentiment Score'
            }
          },
          yAxis:{
            min:'-100',
            max:'100'
          },
        
          xAxis: {
            accessibility: {
              rangeDescription: 'Range: 2010 to 2017'
            },
            
          },
          xAxis:{type:'datetime'},  
          
          legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle'
          },
        
          plotOptions: {
            series: {
              label: {
                connectorAllowed: false
              },
              pointStart: 2010
            }
          },
        
          series: [],
        
          responsive: {
            rules: [{
              condition: {
                maxWidth: 500
              },
              chartOptions: {
                legend: {
                  layout: 'horizontal',
                  align: 'center',
                  verticalAlign: 'bottom'
                }
              }
            }]
          }})
          
          /*A useEffect that passes the hisotricalChart data to the Highchart options and sets the chart
          to display the series for the current favorite.*/
          useEffect(()=>{
            setOptions({series:appContext.historicalChart} )
          },[appContext.historicalChart])
          return(
            <HighchartsReact highcharts={Highcharts} options={options}
             containerProps={{className:props.className}}/>
          )
    
}

export default HighChart;