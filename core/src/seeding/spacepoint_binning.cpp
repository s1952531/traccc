/** TRACCC library, part of the ACTS project (R&D line)
 *
 * (c) 2021-2022 CERN for the benefit of the ACTS project
 *
 * Mozilla Public License Version 2.0
 */

// Library include(s).
#include "traccc/seeding/spacepoint_binning.hpp"

#include <detray/definitions/detail/indexing.hpp>

#include "traccc/definitions/primitives.hpp"
#include "traccc/seeding/spacepoint_binning_helper.hpp"

#include <iostream>
#include <fstream>



namespace traccc {

void write_bin_borders_to_file(const auto& axis, const std::string& filename) {
    std::ofstream bin_borders;

    // clear the file if it exists
    bin_borders.open(filename, std::ios::out);
    bin_borders.close();

    bin_borders.open(filename, std::ios_base::app);
    
    auto num_bins = axis.bins();
    for (unsigned int i = 0; i < num_bins; i++) {
        auto borders = axis.borders(static_cast<detray::dindex>(i));
        bin_borders << borders[0] << "," << borders[1] << std::endl;
    }

    // auto border_values = axis.all_borders();
    // for (scalar border_value : border_values) {
    //     auto ibin = axis.bin(border_value);
    //     std::cout << "ibin: " << ibin << std::endl;
    //     auto borders = axis.borders(ibin);
    //     std::cout << "borders[0]: " << borders[0] << std::endl;
    //     std::cout << "borders[1]: " << borders[1] << std::endl << std::endl;
    //     bin_borders << borders[0] << "," << borders[1] << std::endl;
    // }

    bin_borders.close();

}

void write_r_bins_to_file(const auto& m_config)
{
    std::ofstream r_bin_borders;

    // clear the file if it exists
    r_bin_borders.open("Plotting/SeedingData/r_bin_borders.csv", std::ios::out);
    r_bin_borders.close();

    r_bin_borders.open("Plotting/SeedingData/r_bin_borders.csv", std::ios_base::app);

    auto num_r_bins = m_config.get_num_rbins();
    std::cout << "num_r_bins: " << num_r_bins << std::endl;
    for (unsigned int i = 0; i < num_r_bins + 1; i++) 
    {
        r_bin_borders << i << std::endl;
    }
    
    r_bin_borders.close();
}

spacepoint_binning::spacepoint_binning(
    const seedfinder_config& config, const spacepoint_grid_config& grid_config,
    vecmem::memory_resource& mr)
    : m_config(config),
      m_grid_config(grid_config),
      m_axes(get_axes(grid_config, mr)),
      m_mr(mr) {}

spacepoint_binning::output_type spacepoint_binning::operator()(
    const spacepoint_collection_types::host& sp_collection) const {

    std::cout << "\t\t(inside spacepoint_binning.cpp)" << std::endl;
    std::cout << "\t\tnumber of spacepoints: " << sp_collection.size() << std::endl;

    output_type g2(m_axes.first, m_axes.second, m_mr.get());

    auto& phi_axis = g2.axis_p0();
    auto& z_axis = g2.axis_p1();

    std::cout << "\t\tnumber of phi bins: " << phi_axis.bins() << std::endl;
    std::cout << "\t\tnumber of z bins: " << z_axis.bins() << std::endl;
    std::cout << "\t\tnumber of r bins: " << m_config.get_num_rbins() << std::endl;
    std::cout << "\t\tfor each spacepoint in the event bin it into a given sector prism" << std::endl;
    

    for (unsigned int i = 0; i < sp_collection.size(); i++) {
        const spacepoint& sp = sp_collection[i];
        internal_spacepoint<spacepoint> isp(sp, i, m_config.beamPos);

        if (is_valid_sp(m_config, sp) !=
            detray::detail::invalid_value<size_t>()) {
            const std::size_t bin_index =
                phi_axis.bin(isp.phi()) + phi_axis.bins() * z_axis.bin(isp.z());
            g2.bin(static_cast<detray::dindex>(bin_index))
                .push_back(std::move(isp));
        }

        //write the sp coord to csv file

        std::ofstream spCoords;
        spCoords.open("Plotting/SeedingData/sp.csv", std::ios_base::app);
        spCoords << sp.x() << "," << sp.y() << "," << sp.z() << std::endl;
        spCoords.close();

    }

    std::cout << "\t\tnumber of bins: " << g2.nbins() << std::endl;

    // // loop through all bins in phi_axis and z_axis
    // std::ofstream phi_bin_borders;
    // phi_bin_borders.open("Plotting/SeedingData/phi_bin_borders.csv", std::ios_base::app);

    // auto phi_border_values = phi_axis.all_borders();
    // for (scalar phi_border_value : phi_border_values) {
    //     auto ibin = phi_axis.bin(phi_border_value);
    //     auto borders = phi_axis.borders(ibin);
    //     phi_bin_borders << borders[0] << "," << borders[1] << std::endl;
    // }

    // phi_bin_borders.close();

    // Write phi_axis bin borders to file
    write_bin_borders_to_file(phi_axis, "Plotting/SeedingData/phi_bin_borders.csv");

    // Write z_axis bin borders to file
    write_bin_borders_to_file(z_axis, "Plotting/SeedingData/z_bin_borders.csv");

    // Write r bin borders to file
    write_r_bins_to_file(m_config);

    return g2;
}

}  // namespace traccc
